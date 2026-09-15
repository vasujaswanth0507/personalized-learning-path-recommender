from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LearningPath, LearningPathItem
from app.schemas import LearningPathResponse, LearningPathItemResponse
from app.services.recommendation_service import build_or_refresh_learning_path
from app.services.progress_service import update_and_check_milestones

router = APIRouter(prefix="/paths", tags=["Learning Paths"])

@router.get("/{learner_id}", response_model=LearningPathResponse)
def get_active_path(learner_id: int, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(
        LearningPath.learner_id == learner_id,
        LearningPath.is_active == True
    ).first()

    if not path:
        # Build one if not yet built
        try:
            path = build_or_refresh_learning_path(db, learner_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"No learning path found: {str(e)}")

    items = db.query(LearningPathItem).filter(
        LearningPathItem.path_id == path.id
    ).order_by(LearningPathItem.stage_order).all()

    items_res = [
        LearningPathItemResponse(
            id=i.id,
            stage_order=i.stage_order,
            skill_id=i.skill_id,
            title=i.title,
            description=i.description,
            why_recommended=i.why_recommended,
            prerequisites_summary=i.prerequisites_summary,
            estimated_hours=i.estimated_hours,
            status=i.status,
            is_adaptive_remedial=i.is_adaptive_remedial,
            remedial_reason=i.remedial_reason or "",
            practice_notes=i.practice_notes or ""
        )
        for i in items
    ]

    return LearningPathResponse(
        id=path.id,
        learner_id=path.learner_id,
        title=path.title,
        domain=path.domain,
        target_goal=path.target_goal,
        description=path.description,
        is_active=path.is_active,
        items=items_res
    )

@router.post("/{learner_id}/generate", response_model=LearningPathResponse)
def regenerate_path(learner_id: int, db: Session = Depends(get_db)):
    path = build_or_refresh_learning_path(db, learner_id)
    return get_active_path(learner_id, db)

@router.patch("/items/{item_id}/status")
def update_item_status(item_id: int, status: str = Body(..., embed=True), db: Session = Depends(get_db)):
    item = db.query(LearningPathItem).filter(LearningPathItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Path item not found")

    valid_statuses = ["completed", "in_progress", "available", "locked", "skipped"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    item.status = status
    db.commit()

    # If completed or skipped, unlock the next item
    if status in ["completed", "skipped"]:
        next_item = db.query(LearningPathItem).filter(
            LearningPathItem.path_id == item.path_id,
            LearningPathItem.stage_order > item.stage_order,
            LearningPathItem.status != "completed"
        ).order_by(LearningPathItem.stage_order).first()
        if next_item and next_item.status == "locked":
            next_item.status = "in_progress"
            db.commit()

        # Update milestones
        update_and_check_milestones(db, item.path.learner_id)

    return {"message": f"Item '{item.title}' updated to '{status}'", "item_id": item.id, "new_status": item.status}
