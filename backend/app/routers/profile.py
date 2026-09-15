import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Learner
from app.schemas import (
    LearnerProfileCreate, LearnerProfileUpdate, LearnerProfileResponse
)
from app.services.recommendation_service import build_or_refresh_learning_path

router = APIRouter(prefix="/profile", tags=["Learner Profile"])

def format_learner_response(learner: Learner) -> LearnerProfileResponse:
    return LearnerProfileResponse(
        id=learner.id,
        name=learner.name,
        target_goal=learner.target_goal,
        direction=learner.direction,
        current_knowledge=json.loads(learner.current_knowledge) if learner.current_knowledge else [],
        current_level=learner.current_level,
        available_time=learner.available_time,
        target_timeline=learner.target_timeline,
        learning_preference=learner.learning_preference,
        weak_areas=json.loads(learner.weak_areas) if learner.weak_areas else [],
        areas_to_explore=json.loads(learner.areas_to_explore) if learner.areas_to_explore else [],
        notes=learner.notes or "",
        created_at=learner.created_at.isoformat() if learner.created_at else "",
        updated_at=learner.updated_at.isoformat() if learner.updated_at else ""
    )

@router.post("", response_model=LearnerProfileResponse)
def create_learner_profile(data: LearnerProfileCreate, db: Session = Depends(get_db)):
    learner = Learner(
        name=data.name,
        target_goal=data.target_goal,
        direction=data.direction,
        current_knowledge=json.dumps(data.current_knowledge),
        current_level=data.current_level,
        available_time=data.available_time,
        target_timeline=data.target_timeline,
        learning_preference=data.learning_preference,
        weak_areas=json.dumps(data.weak_areas),
        areas_to_explore=json.dumps(data.areas_to_explore),
        notes=data.notes
    )
    db.add(learner)
    db.commit()
    db.refresh(learner)

    # Immediately build personalized path
    build_or_refresh_learning_path(db, learner.id)

    return format_learner_response(learner)

@router.get("", response_model=List[LearnerProfileResponse])
def list_learners(db: Session = Depends(get_db)):
    learners = db.query(Learner).order_by(Learner.created_at.desc()).all()
    return [format_learner_response(l) for l in learners]

@router.get("/{learner_id}", response_model=LearnerProfileResponse)
def get_learner_profile(learner_id: int, db: Session = Depends(get_db)):
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return format_learner_response(learner)

@router.put("/{learner_id}", response_model=LearnerProfileResponse)
def update_learner_profile(
    learner_id: int,
    data: LearnerProfileUpdate,
    regenerate_path: bool = False,
    db: Session = Depends(get_db)
):
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    if data.name is not None:
        learner.name = data.name
    if data.target_goal is not None:
        learner.target_goal = data.target_goal
    if data.direction is not None:
        learner.direction = data.direction
    if data.current_knowledge is not None:
        learner.current_knowledge = json.dumps(data.current_knowledge)
    if data.current_level is not None:
        learner.current_level = data.current_level
    if data.available_time is not None:
        learner.available_time = data.available_time
    if data.target_timeline is not None:
        learner.target_timeline = data.target_timeline
    if data.learning_preference is not None:
        learner.learning_preference = data.learning_preference
    if data.weak_areas is not None:
        learner.weak_areas = json.dumps(data.weak_areas)
    if data.areas_to_explore is not None:
        learner.areas_to_explore = json.dumps(data.areas_to_explore)
    if data.notes is not None:
        learner.notes = data.notes

    db.commit()
    db.refresh(learner)

    if regenerate_path:
        build_or_refresh_learning_path(db, learner.id)

    return format_learner_response(learner)

@router.delete("/{learner_id}")
def delete_learner_profile(learner_id: int, db: Session = Depends(get_db)):
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    
    try:
        db.delete(learner)
        db.commit()
        return {"status": "success", "message": "Profile and all associated data permanently deleted."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete profile: {str(e)}")

@router.post("/reset")
def reset_database(db: Session = Depends(get_db)):
    try:
        learners = db.query(Learner).all()
        for learner in learners:
            db.delete(learner)
        db.commit()
        return {"status": "success", "message": f"Reset completed. Deleted {len(learners)} learner profiles and all associated records."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database reset failed: {str(e)}")
