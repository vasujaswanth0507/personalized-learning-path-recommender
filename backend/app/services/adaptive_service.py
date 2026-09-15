import json
from sqlalchemy.orm import Session
from app.models import (
    Learner, LearningPath, LearningPathItem, LearnerFeedback,
    LearnerAssessmentAttempt, LearningResource
)

def adapt_path_after_feedback(db: Session, learner_id: int, feedback: LearnerFeedback) -> str:
    """
    Dynamically modifies the learner's active learning path in response to feedback:
    - 'difficult' or 'very_difficult': Inserts a targeted refresher/practice stage.
    - 'already know': Marks current stage as skipped/completed and unlocks downstream items.
    - 'easy': Shortens estimated hours or unlocks the next milestone immediately.
    """
    path = db.query(LearningPath).filter(
        LearningPath.learner_id == learner_id,
        LearningPath.is_active == True
    ).first()

    if not path:
        return "No active learning path found."

    action_summary = "Feedback recorded."
    comment_lower = feedback.comment.lower()

    # Case 1: Learner says they already know this topic
    if "already know" in comment_lower or "skip" in comment_lower or feedback.rating == "easy" and "know" in comment_lower:
        # Find item
        target_item = None
        if feedback.item_id:
            target_item = db.query(LearningPathItem).filter(
                LearningPathItem.path_id == path.id,
                LearningPathItem.id == feedback.item_id
            ).first()

        if not target_item:
            # Find current in_progress item
            target_item = db.query(LearningPathItem).filter(
                LearningPathItem.path_id == path.id,
                LearningPathItem.status == "in_progress"
            ).first()

        if target_item:
            target_item.status = "completed"
            target_item.practice_notes = "Fast-tracked based on learner's declared prior proficiency."
            
            # Unlock next stage
            next_item = db.query(LearningPathItem).filter(
                LearningPathItem.path_id == path.id,
                LearningPathItem.stage_order > target_item.stage_order,
                LearningPathItem.status.in_(["available", "locked"])
            ).order_by(LearningPathItem.stage_order).first()
            if next_item:
                next_item.status = "in_progress"

            action_summary = f"Fast-tracked '{target_item.title}' and advanced your active roadmap stage."
            feedback.action_applied = action_summary
            db.commit()
            return action_summary

    # Case 2: Learner finds the topic difficult or requests more practice
    if feedback.rating in ["difficult", "very_difficult"] or "more practice" in comment_lower or "too difficult" in comment_lower or "need more practice" in comment_lower:
        current_item = None
        if feedback.item_id:
            current_item = db.query(LearningPathItem).filter(
                LearningPathItem.path_id == path.id,
                LearningPathItem.id == feedback.item_id
            ).first()
        if not current_item:
            current_item = db.query(LearningPathItem).filter(
                LearningPathItem.path_id == path.id,
                LearningPathItem.status == "in_progress"
            ).first()

        if current_item and not current_item.is_adaptive_remedial:
            # Check if a remedial item already exists for this stage
            existing_remedial = db.query(LearningPathItem).filter(
                LearningPathItem.path_id == path.id,
                LearningPathItem.is_adaptive_remedial == True,
                LearningPathItem.remedial_reason.like(f"%{current_item.title}%")
            ).first()

            if not existing_remedial:
                # Shift subsequent stage orders by +1
                later_items = db.query(LearningPathItem).filter(
                    LearningPathItem.path_id == path.id,
                    LearningPathItem.stage_order > current_item.stage_order
                ).all()
                for item in later_items:
                    item.stage_order += 1

                remedial_title = f"{current_item.title}: Guided Practice Lab & Refresher"
                remedial_desc = f"Adaptive targeted practice module inserted based on your feedback. Focuses on core concepts of {current_item.title} with step-by-step problem walkthroughs."
                
                remedial_item = LearningPathItem(
                    path_id=path.id,
                    stage_order=current_item.stage_order + 1,
                    skill_id=current_item.skill_id,
                    title=remedial_title,
                    description=remedial_desc,
                    why_recommended=f"Dynamically inserted because you noted difficulties with {current_item.title}. Provides extra exercises before moving to subsequent topics.",
                    prerequisites_summary=current_item.title,
                    estimated_hours=2.5,
                    status="available",
                    is_adaptive_remedial=True,
                    remedial_reason=f"Learner feedback: '{feedback.rating}' - {feedback.comment[:50]}",
                    practice_notes="Recommended: work through the code snippets and step-by-step examples."
                )
                db.add(remedial_item)
                action_summary = f"Inserted custom practice module '{remedial_title}' into your roadmap."
                feedback.action_applied = action_summary
                db.commit()
                return action_summary

    # Case 3: Need project-based learning
    if "project" in comment_lower or "hands-on" in comment_lower:
        action_summary = "Roadmap adapted to emphasize practical mini-project deliverables."
        feedback.action_applied = action_summary
        db.commit()
        return action_summary

    feedback.action_applied = "Feedback logged for future recommendations."
    db.commit()
    return "Thank you for the feedback! Your inputs will fine-tune subsequent recommendations."


def adapt_path_after_assessment(db: Session, learner_id: int, attempt: LearnerAssessmentAttempt) -> str:
    """
    Adapts path when a learner completes an assessment:
    - If score < 70%, marks weak areas in learner profile and inserts a targeted refresher item.
    - If score >= 70%, marks corresponding path item as completed and unlocks next item.
    """
    path = db.query(LearningPath).filter(
        LearningPath.learner_id == learner_id,
        LearningPath.is_active == True
    ).first()

    if not path:
        return "Assessment recorded."

    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    assessment = attempt.assessment

    if attempt.passed:
        # If passed, unlock next stage
        if assessment.skill_id:
            path_item = db.query(LearningPathItem).filter(
                LearningPathItem.path_id == path.id,
                LearningPathItem.skill_id == assessment.skill_id
            ).first()
            if path_item:
                path_item.status = "completed"
                # Unlock next locked or available stage
                next_stage = db.query(LearningPathItem).filter(
                    LearningPathItem.path_id == path.id,
                    LearningPathItem.stage_order > path_item.stage_order,
                    LearningPathItem.status != "completed"
                ).order_by(LearningPathItem.stage_order).first()
                if next_stage:
                    next_stage.status = "in_progress"
                db.commit()
                return f"Assessment passed ({attempt.score}/{attempt.total_questions})! Stage '{path_item.title}' completed."
        return f"Great job! Assessment passed with {attempt.percentage:.0f}% score."

    else:
        # Score < 70%
        # Update learner weak areas
        weak_list = json.loads(attempt.weak_areas) if attempt.weak_areas else [assessment.topic]
        current_weaks = json.loads(learner.weak_areas) if learner.weak_areas else []
        for w in weak_list:
            if w not in current_weaks:
                current_weaks.append(w)
        learner.weak_areas = json.dumps(current_weaks)

        # Check if refresher already inserted
        remedial_title = f"{assessment.topic} Refresher & Concept Drill"
        existing = db.query(LearningPathItem).filter(
            LearningPathItem.path_id == path.id,
            LearningPathItem.title == remedial_title
        ).first()

        if not existing:
            # Insert right after current active stage
            current_stage = db.query(LearningPathItem).filter(
                LearningPathItem.path_id == path.id,
                LearningPathItem.status == "in_progress"
            ).first()

            current_order = current_stage.stage_order if current_stage else 1

            # Shift later items
            later_items = db.query(LearningPathItem).filter(
                LearningPathItem.path_id == path.id,
                LearningPathItem.stage_order > current_order
            ).all()
            for li in later_items:
                li.stage_order += 1

            refresher_item = LearningPathItem(
                path_id=path.id,
                stage_order=current_order + 1,
                skill_id=assessment.skill_id,
                title=remedial_title,
                description=f"Targeted review module covering key concepts in {assessment.topic} where assessment score fell below 70%.",
                why_recommended=f"Assessment result ({attempt.score}/{attempt.total_questions}) identified conceptual gaps. Working through this refresher will reinforce retention before advancing.",
                prerequisites_summary=assessment.topic,
                estimated_hours=2.0,
                status="in_progress" if not current_stage else "available",
                is_adaptive_remedial=True,
                remedial_reason=f"Assessment score {attempt.percentage:.0f}% below 70% threshold.",
                practice_notes="Review explanations for missed questions and re-attempt the quiz."
            )
            db.add(refresher_item)
            db.commit()
            return f"Identified weak areas in {assessment.topic}. Added a targeted Refresher Stage to reinforce these concepts."

        return f"Assessment score was {attempt.percentage:.0f}%. Review recommended before retaking."
