from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MentorMessage
from app.schemas import MentorChatRequest, MentorChatResponse
from app.services.mentor_service import ask_ai_mentor

router = APIRouter(prefix="/mentor", tags=["AI Mentor"])

@router.post("/{learner_id}/chat", response_model=MentorChatResponse)
async def chat_with_mentor(
    learner_id: int,
    req: MentorChatRequest,
    db: Session = Depends(get_db)
):
    result = await ask_ai_mentor(
        db=db,
        learner_id=learner_id,
        user_message=req.message,
        current_stage=req.current_stage,
        context_topic=req.context_topic
    )
    return MentorChatResponse(**result)

@router.get("/{learner_id}/history")
def get_mentor_history(learner_id: int, db: Session = Depends(get_db)):
    messages = db.query(MentorMessage).filter(
        MentorMessage.learner_id == learner_id
    ).order_by(MentorMessage.timestamp.asc()).all()

    return [
        {
            "id": m.id,
            "sender": m.sender,
            "content": m.content,
            "context_tag": m.context_tag,
            "timestamp": m.timestamp.strftime("%b %d, %H:%M") if m.timestamp else ""
        }
        for m in messages
    ]
