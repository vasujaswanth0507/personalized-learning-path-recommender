from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LearnerFeedback
from app.schemas import FeedbackSubmitRequest, FeedbackResponse
from app.services.adaptive_service import adapt_path_after_feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("", response_model=FeedbackResponse)
def submit_feedback(
    learner_id: int = Query(...),
    data: FeedbackSubmitRequest = None,
    db: Session = Depends(get_db)
):
    if not data:
        raise HTTPException(status_code=400, detail="Feedback payload required")

    feedback = LearnerFeedback(
        learner_id=learner_id,
        item_type=data.item_type,
        item_id=data.item_id,
        item_title=data.item_title,
        rating=data.rating,
        comment=data.comment
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # Dynamic adaptation
    action_applied = adapt_path_after_feedback(db, learner_id, feedback)

    return FeedbackResponse(
        id=feedback.id,
        rating=feedback.rating,
        comment=feedback.comment,
        action_applied=action_applied,
        created_at=feedback.created_at.strftime("%b %d, %H:%M") if feedback.created_at else ""
    )

@router.get("/{learner_id}", response_model=List[FeedbackResponse])
def get_learner_feedback(learner_id: int, db: Session = Depends(get_db)):
    fbs = db.query(LearnerFeedback).filter(
        LearnerFeedback.learner_id == learner_id
    ).order_by(LearnerFeedback.created_at.desc()).all()

    return [
        FeedbackResponse(
            id=f.id,
            rating=f.rating,
            comment=f.comment,
            action_applied=f.action_applied or "",
            created_at=f.created_at.strftime("%b %d, %H:%M") if f.created_at else ""
        )
        for f in fbs
    ]
