import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, LearnerProjectProgress
from app.schemas import ProjectResponse, ProjectProgressUpdate
from app.services.progress_service import update_and_check_milestones

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
def list_projects(
    domain: Optional[str] = Query(None),
    learner_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Project)
    if domain:
        query = query.filter(Project.domain == domain)

    projects = query.all()

    progress_map = {}
    if learner_id:
        progs = db.query(LearnerProjectProgress).filter(LearnerProjectProgress.learner_id == learner_id).all()
        for p in progs:
            progress_map[p.project_id] = p

    res_list = []
    for pr in projects:
        user_p = progress_map.get(pr.id)
        res_list.append(ProjectResponse(
            id=pr.id,
            title=pr.title,
            domain=pr.domain,
            topic=pr.topic or "",
            objective=pr.objective,
            difficulty=pr.difficulty,
            required_skills=pr.required_skills,
            prerequisites=pr.prerequisites,
            estimated_hours=pr.estimated_hours,
            suggested_steps=json.loads(pr.suggested_steps) if pr.suggested_steps else [],
            expected_outcome=pr.expected_outcome,
            user_status=user_p.status if user_p else "not_started",
            repo_url=user_p.repo_url if user_p and user_p.repo_url else "",
            notes=user_p.notes if user_p and user_p.notes else ""
        ))

    return res_list

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_detail(
    project_id: int,
    learner_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    pr = db.query(Project).filter(Project.id == project_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Project not found")

    user_p = None
    if learner_id:
        user_p = db.query(LearnerProjectProgress).filter(
            LearnerProjectProgress.learner_id == learner_id,
            LearnerProjectProgress.project_id == project_id
        ).first()

    return ProjectResponse(
        id=pr.id,
        title=pr.title,
        domain=pr.domain,
        topic=pr.topic or "",
        objective=pr.objective,
        difficulty=pr.difficulty,
        required_skills=pr.required_skills,
        prerequisites=pr.prerequisites,
        estimated_hours=pr.estimated_hours,
        suggested_steps=json.loads(pr.suggested_steps) if pr.suggested_steps else [],
        expected_outcome=pr.expected_outcome,
        user_status=user_p.status if user_p else "not_started",
        repo_url=user_p.repo_url if user_p and user_p.repo_url else "",
        notes=user_p.notes if user_p and user_p.notes else ""
    )

@router.post("/{project_id}/progress")
def update_project_progress(
    project_id: int,
    learner_id: int = Query(...),
    data: ProjectProgressUpdate = None,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    prog = db.query(LearnerProjectProgress).filter(
        LearnerProjectProgress.learner_id == learner_id,
        LearnerProjectProgress.project_id == project_id
    ).first()

    if not prog:
        prog = LearnerProjectProgress(
            learner_id=learner_id,
            project_id=project_id,
            status=data.status if data else "completed",
            repo_url=data.repo_url if data else "",
            notes=data.notes if data else ""
        )
        db.add(prog)
    else:
        if data:
            prog.status = data.status
            if data.repo_url is not None:
                prog.repo_url = data.repo_url
            if data.notes is not None:
                prog.notes = data.notes

    db.commit()
    update_and_check_milestones(db, learner_id)
    return {"message": "Project progress updated", "project_id": project_id, "status": prog.status}
