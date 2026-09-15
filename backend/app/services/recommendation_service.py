import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models import (
    Learner, Skill, SkillPrerequisite, LearningPath, LearningPathItem,
    LearningResource, LearnerProgress, LearnerFeedback, LearnerAssessmentAttempt
)

def normalize_skill_name(name: str) -> str:
    """Normalize skill name for fuzzy matching against learner's known skills."""
    return name.lower().replace("&", "and").replace("-", " ").strip()

def is_skill_known_by_learner(skill_name: str, known_skills: List[str]) -> bool:
    """Checks if a skill is in the learner's declared prior knowledge."""
    norm_target = normalize_skill_name(skill_name)
    for k in known_skills:
        norm_k = normalize_skill_name(k)
        if norm_k in norm_target or norm_target in norm_k:
            return True
        # Check specific tokens
        if ("linux" in norm_k and "linux" in norm_target) or \
           ("python" in norm_k and "python" in norm_target) or \
           ("aws" in norm_k and "aws" in norm_target) or \
           ("docker" in norm_k and "docker" in norm_target) or \
           ("react" in norm_k and "react" in norm_target) or \
           ("sql" in norm_k and "sql" in norm_target):
            return True
    return False

def calculate_stage_score(
    skill: Skill,
    prereqs_met: bool,
    is_known: bool,
    learner_level: str,
    feedback_penalty: float = 0.0
) -> float:
    """
    Transparent scoring function for ranking learning stages:
    Score = (Goal Relevance * 40) + (Prerequisite Status * 30) + (Difficulty Alignment * 20) - (Feedback Penalty)
    """
    relevance_score = 40.0

    # Prerequisite status
    prereq_score = 30.0 if prereqs_met else 5.0

    # Difficulty fit
    level_map = {"Beginner": 1, "Early Intermediate": 2, "Intermediate": 2, "Advanced": 3}
    skill_diff_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    
    learner_val = level_map.get(learner_level, 1)
    skill_val = skill_diff_map.get(skill.difficulty_level, 1)
    
    diff_distance = abs(learner_val - skill_val)
    difficulty_score = max(5.0, 20.0 - (diff_distance * 7.0))

    score = relevance_score + prereq_score + difficulty_score - feedback_penalty
    return round(score, 2)

def generate_recommendation_explanation(
    skill: Skill,
    prerequisites: List[Skill],
    is_known: bool,
    learner: Learner,
    known_skills: List[str],
    stage_idx: int
) -> str:
    """
    Generates human-readable, context-rich 'Why this recommendation?' explanation
    grounded in learner profile facts and prerequisite dependency logic.
    """
    if is_known:
        return (
            f"You indicated prior familiarity with {skill.name}. We have marked this foundational topic as completed "
            f"so you can immediately start with more advanced, high-leverage material."
        )

    # Prerequisite-aware explanation
    if prerequisites:
        prereq_names = ", ".join([p.name for p in prerequisites])
        known_prereq = [p.name for p in prerequisites if is_skill_known_by_learner(p.name, known_skills)]
        
        if known_prereq:
            return (
                f"You already have experience with {', '.join(known_prereq)}, allowing you to unlock {skill.name}. "
                f"This topic directly builds on those fundamentals and is essential for achieving your goal of {learner.target_goal}."
            )
        else:
            return (
                f"{skill.name} was scheduled following {prereq_names} to ensure you have the required conceptual foundations "
                f"before tackling real-world implementation."
            )

    if stage_idx == 0:
        return (
            f"{skill.name} serves as the primary stepping stone for {learner.direction}. "
            f"Mastering this foundational topic provides the toolkit required for all downstream hands-on projects."
        )

    return (
        f"This topic was prioritized based on your target goal '{learner.target_goal}' and your preferred "
        f"{learner.learning_preference.lower()} learning style."
    )

def build_or_refresh_learning_path(db: Session, learner_id: int) -> LearningPath:
    """
    Constructs a personalized, dependency-respecting learning path for the learner.
    Skips or credits topics the learner already knows, sets the first uncompleted eligible topic
    as 'in_progress', and locks downstream topics whose prerequisites are unmet.
    """
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise ValueError(f"Learner {learner_id} not found")

    known_skills = json.loads(learner.current_knowledge) if learner.current_knowledge else []

    # Find relevant skills matching learner's direction
    domain_skills = db.query(Skill).filter(Skill.domain == learner.direction).all()
    if not domain_skills:
        # Fallback to all skills or Cloud / DevOps
        domain_skills = db.query(Skill).filter(Skill.domain == "Cloud / DevOps").all()

    # Load all prerequisites
    all_prereqs = db.query(SkillPrerequisite).all()
    # Map: skill_id -> list of prerequisite_skill_ids
    prereq_map: Dict[int, List[int]] = {}
    for p in all_prereqs:
        prereq_map.setdefault(p.skill_id, []).append(p.prerequisite_skill_id)

    # Deactivate existing paths
    existing_paths = db.query(LearningPath).filter(LearningPath.learner_id == learner_id).all()
    for ep in existing_paths:
        ep.is_active = False
    db.commit()

    # Create new LearningPath
    new_path = LearningPath(
        learner_id=learner.id,
        title=f"{learner.direction} Mastery Roadmap",
        domain=learner.direction,
        target_goal=learner.target_goal,
        description=f"Personalized path generated for {learner.name} towards {learner.target_goal} with an estimated {learner.available_time} commitment.",
        is_active=True
    )
    db.add(new_path)
    db.commit()

    # Sort domain skills respecting dependencies (Topological ordering)
    skill_dict = {s.id: s for s in domain_skills}
    ordered_skills: List[Skill] = []
    visited = set()

    def visit(s_id: int):
        if s_id in visited or s_id not in skill_dict:
            return
        # Visit prereqs first
        for req_id in prereq_map.get(s_id, []):
            if req_id in skill_dict:
                visit(req_id)
        visited.add(s_id)
        ordered_skills.append(skill_dict[s_id])

    for s in domain_skills:
        visit(s.id)

    # Now create LearningPathItems with proper status and rationale
    has_set_current = False
    completed_skill_ids = set()

    for idx, skill in enumerate(ordered_skills):
        is_known = is_skill_known_by_learner(skill.name, known_skills)
        req_ids = prereq_map.get(skill.id, [])
        req_skills = [db.query(Skill).filter(Skill.id == rid).first() for rid in req_ids]
        req_skills = [r for r in req_skills if r is not None]

        req_names = ", ".join([r.name for r in req_skills]) if req_skills else "None"

        # Determine status
        prereqs_satisfied = all(rid in completed_skill_ids or is_skill_known_by_learner(skill_dict[rid].name, known_skills) for rid in req_ids if rid in skill_dict)

        if is_known:
            status = "completed"
            completed_skill_ids.add(skill.id)
        elif not prereqs_satisfied:
            status = "locked"
        elif not has_set_current:
            status = "in_progress"
            has_set_current = True
        else:
            status = "available"

        explanation = generate_recommendation_explanation(
            skill=skill,
            prerequisites=req_skills,
            is_known=is_known,
            learner=learner,
            known_skills=known_skills,
            stage_idx=idx
        )

        item = LearningPathItem(
            path_id=new_path.id,
            stage_order=idx + 1,
            skill_id=skill.id,
            title=skill.name,
            description=skill.description,
            why_recommended=explanation,
            prerequisites_summary=req_names,
            estimated_hours=4.5,
            status=status,
            is_adaptive_remedial=False,
            remedial_reason="",
            practice_notes=""
        )
        db.add(item)

    db.commit()
    db.refresh(new_path)
    return new_path
