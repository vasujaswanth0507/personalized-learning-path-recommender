from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LearningResource, LearnerProgress
from app.schemas import LearningResourceResponse, ResourceProgressUpdate
from app.services.progress_service import update_and_check_milestones

router = APIRouter(prefix="/resources", tags=["Learning Resources"])

@router.get("", response_model=List[LearningResourceResponse])
def list_resources(
    domain: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    learner_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(LearningResource)
    if domain:
        query = query.filter(LearningResource.domain == domain)
    if topic:
        query = query.filter(LearningResource.topic.ilike(f"%{topic}%"))
    if difficulty:
        query = query.filter(LearningResource.difficulty == difficulty)

    resources = query.all()

    # If learner_id provided, fetch their statuses
    progress_map = {}
    if learner_id:
        progs = db.query(LearnerProgress).filter(LearnerProgress.learner_id == learner_id).all()
        for p in progs:
            progress_map[p.resource_id] = p.status

    res_list = []
    for r in resources:
        res_list.append(LearningResourceResponse(
            id=r.id,
            title=r.title,
            topic=r.topic,
            domain=r.domain,
            description=r.description,
            difficulty=r.difficulty,
            prerequisites_summary=r.prerequisites_summary,
            estimated_hours=r.estimated_hours,
            resource_type=r.resource_type,
            url=r.url,
            user_status=progress_map.get(r.id, "not_started"),
            key_takeaways=r.key_takeaways or "",
            skill_id=r.skill_id
        ))

    return res_list

@router.get("/{resource_id}", response_model=LearningResourceResponse)
def get_resource_detail(
    resource_id: int,
    learner_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    r = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resource not found")

    user_status = "not_started"
    if learner_id:
        p = db.query(LearnerProgress).filter(
            LearnerProgress.learner_id == learner_id,
            LearnerProgress.resource_id == resource_id
        ).first()
        if p:
            user_status = p.status

    return LearningResourceResponse(
        id=r.id,
        title=r.title,
        topic=r.topic,
        domain=r.domain,
        description=r.description,
        difficulty=r.difficulty,
        prerequisites_summary=r.prerequisites_summary,
        estimated_hours=r.estimated_hours,
        resource_type=r.resource_type,
        url=r.url,
        user_status=user_status,
        key_takeaways=r.key_takeaways or "",
        skill_id=r.skill_id
    )

@router.post("/{resource_id}/progress")
def update_resource_progress(
    resource_id: int,
    learner_id: int = Query(...),
    data: ResourceProgressUpdate = None,
    db: Session = Depends(get_db)
):
    resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    prog = db.query(LearnerProgress).filter(
        LearnerProgress.learner_id == learner_id,
        LearnerProgress.resource_id == resource_id
    ).first()

    if not prog:
        prog = LearnerProgress(
            learner_id=learner_id,
            resource_id=resource_id,
            status=data.status if data else "completed",
            time_spent_minutes=data.time_spent_minutes if data else 30,
            notes=data.notes if data else ""
        )
        db.add(prog)
    else:
        if data:
            prog.status = data.status
            prog.time_spent_minutes += data.time_spent_minutes
            if data.notes:
                prog.notes = data.notes

    db.commit()
    update_and_check_milestones(db, learner_id)
    return {"message": "Progress recorded", "resource_id": resource_id, "status": prog.status}
