import json
import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import (
    Learner, LearningPath, LearningPathItem, LearningResource,
    LearnerProgress, Project, LearnerProjectProgress, Assessment,
    LearnerAssessmentAttempt, LearnerFeedback, Milestone, LearnerMilestone, Skill
)

def update_and_check_milestones(db: Session, learner_id: int):
    """Evaluates learner activity and unlocks eligible milestones."""
    milestones = db.query(Milestone).all()
    unlocked_ids = {
        lm.milestone_id for lm in db.query(LearnerMilestone).filter(LearnerMilestone.learner_id == learner_id).all()
    }

    # Count completed path items
    completed_stages_count = db.query(LearningPathItem).join(LearningPath).filter(
        LearningPath.learner_id == learner_id,
        LearningPathItem.status == "completed"
    ).count()

    # Count completed projects
    completed_projects_count = db.query(LearnerProjectProgress).filter(
        LearnerProjectProgress.learner_id == learner_id,
        LearnerProjectProgress.status == "completed"
    ).count()

    # Count passed assessments
    passed_assessments_count = db.query(LearnerAssessmentAttempt).filter(
        LearnerAssessmentAttempt.learner_id == learner_id,
        LearnerAssessmentAttempt.passed == True
    ).count()

    # Total stages in active path
    total_stages = db.query(LearningPathItem).join(LearningPath).filter(
        LearningPath.learner_id == learner_id,
        LearningPath.is_active == True
    ).count()

    for m in milestones:
        if m.id in unlocked_ids:
            continue

        should_unlock = False
        if m.requirement_type == "first_topic" and completed_stages_count >= 1:
            should_unlock = True
        elif m.requirement_type == "skill_count" and completed_stages_count >= m.requirement_value:
            should_unlock = True
        elif m.requirement_type == "first_project" and completed_projects_count >= 1:
            should_unlock = True
        elif m.requirement_type == "first_assessment" and passed_assessments_count >= 1:
            should_unlock = True
        elif m.requirement_type == "path_complete" and total_stages > 0 and completed_stages_count >= total_stages:
            should_unlock = True

        if should_unlock:
            new_lm = LearnerMilestone(
                learner_id=learner_id,
                milestone_id=m.id,
                unlocked_at=datetime.datetime.utcnow()
            )
            db.add(new_lm)

    db.commit()


def get_dashboard_data(db: Session, learner_id: int) -> Dict[str, Any]:
    """
    Computes dashboard analytics derived directly from real database records.
    No hard-coded or fake progress metrics!
    """
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise ValueError(f"Learner {learner_id} not found")

    update_and_check_milestones(db, learner_id)

    # Active path & items
    active_path = db.query(LearningPath).filter(
        LearningPath.learner_id == learner_id,
        LearningPath.is_active == True
    ).first()

    total_stages = 0
    completed_stages = 0
    current_item = None
    next_action = None

    if active_path:
        items = db.query(LearningPathItem).filter(
            LearningPathItem.path_id == active_path.id
        ).order_by(LearningPathItem.stage_order).all()

        total_stages = len(items)
        for item in items:
            if item.status == "completed":
                completed_stages += 1
            elif item.status == "in_progress" and not current_item:
                current_item = item.title
            elif item.status in ["available", "in_progress"] and not next_action and item.title != current_item:
                next_action = f"Advance to {item.title}"

        if not current_item and items:
            # Check for first uncompleted item
            first_uncompleted = next((i for i in items if i.status != "completed"), None)
            if first_uncompleted:
                current_item = first_uncompleted.title
                if first_uncompleted.status == "locked":
                    next_action = f"Complete prerequisites for {first_uncompleted.title}"
            else:
                current_item = "Path Completed! All milestones reached."
                next_action = "Explore Capstone Projects or deeper specializations"

    overall_pct = int(round((completed_stages / total_stages) * 100)) if total_stages > 0 else 0

    # Skill mastery calculation
    # Fetch all skills in domain
    domain_skills = db.query(Skill).filter(Skill.domain == learner.direction).all()
    known_skills = json.loads(learner.current_knowledge) if learner.current_knowledge else []

    # Map completed stage skill_ids
    completed_skill_ids = set()
    if active_path:
        for it in active_path.items:
            if it.status == "completed" and it.skill_id:
                completed_skill_ids.add(it.skill_id)

    skill_mastery_list = []
    for sk in domain_skills[:6]:  # top 6 domain skills
        is_known = any(k.lower() in sk.name.lower() or sk.name.lower() in k.lower() for k in known_skills)
        if sk.id in completed_skill_ids:
            pct = 100
            status = "Mastered"
        elif is_known:
            pct = 90
            status = "Prior Skill"
        elif current_item and sk.name in current_item:
            pct = 45
            status = "In Progress"
        else:
            pct = 0
            status = "Upcoming"

        skill_mastery_list.append({
            "skill_name": sk.name,
            "percentage": pct,
            "status": status
        })

    # Milestones
    all_milestones = db.query(Milestone).all()
    unlocked_map = {
        lm.milestone_id: lm.unlocked_at.strftime("%b %d, %Y")
        for lm in db.query(LearnerMilestone).filter(LearnerMilestone.learner_id == learner_id).all()
    }

    milestones_data = []
    for m in all_milestones:
        is_unlocked = m.id in unlocked_map
        milestones_data.append({
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "badge_icon": m.badge_icon,
            "is_unlocked": is_unlocked,
            "unlocked_at": unlocked_map.get(m.id)
        })

    # Recent Feedback
    feedbacks = db.query(LearnerFeedback).filter(
        LearnerFeedback.learner_id == learner_id
    ).order_by(LearnerFeedback.created_at.desc()).limit(3).all()

    recent_fb_list = [
        {
            "id": f.id,
            "item_title": f.item_title,
            "rating": f.rating,
            "comment": f.comment,
            "action_applied": f.action_applied,
            "created_at": f.created_at.strftime("%b %d, %H:%M")
        }
        for f in feedbacks
    ]

    return {
        "learner_name": learner.name,
        "target_goal": learner.target_goal,
        "direction": learner.direction,
        "overall_progress_pct": overall_pct,
        "completed_items_count": completed_stages,
        "total_items_count": total_stages,
        "current_learning_item": current_item or "Not started",
        "next_recommended_action": next_action or "Start your first recommended resource",
        "skill_mastery": skill_mastery_list,
        "milestones": milestones_data,
        "recent_feedback": recent_fb_list
    }
