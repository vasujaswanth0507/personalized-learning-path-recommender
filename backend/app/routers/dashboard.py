from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import DashboardStatsResponse
from app.services.progress_service import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/{learner_id}", response_model=DashboardStatsResponse)
def get_learner_dashboard(learner_id: int, db: Session = Depends(get_db)):
    try:
        stats = get_dashboard_data(db, learner_id)
        return DashboardStatsResponse(**stats)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
