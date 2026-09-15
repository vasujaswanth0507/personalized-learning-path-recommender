from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import OnboardingRequest, OnboardingResponse
from app.services.onboarding_service import process_onboarding_turn

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.post("/chat", response_model=OnboardingResponse)
async def chat_onboarding(req: OnboardingRequest, db: Session = Depends(get_db)):
    history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
    result = await process_onboarding_turn(
        db=db,
        message=req.message,
        history=history_dicts,
        current_extracted=req.current_extracted
    )
    return OnboardingResponse(**result)
