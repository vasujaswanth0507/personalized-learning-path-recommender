import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    Assessment, AssessmentQuestion, LearnerAssessmentAttempt
)
from app.schemas import (
    AssessmentResponse, AssessmentQuestionResponse,
    AssessmentSubmissionRequest, AssessmentSubmissionResult, QuestionResultItem
)
from app.services.adaptive_service import adapt_path_after_assessment
from app.services.progress_service import update_and_check_milestones

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.get("", response_model=List[AssessmentResponse])
def list_assessments(
    domain: Optional[str] = Query(None),
    skill_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Assessment)
    if domain:
        query = query.filter(Assessment.domain == domain)
    if skill_id:
        query = query.filter(Assessment.skill_id == skill_id)

    assessments = query.all()
    res = []
    for a in assessments:
        questions = [
            AssessmentQuestionResponse(
                id=q.id,
                question_text=q.question_text,
                options=json.loads(q.options) if q.options else []
            )
            for q in a.questions
        ]
        res.append(AssessmentResponse(
            id=a.id,
            title=a.title,
            topic=a.topic,
            domain=a.domain,
            passing_percentage=a.passing_percentage,
            description=a.description or "",
            questions=questions
        ))
    return res

@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment_detail(assessment_id: int, db: Session = Depends(get_db)):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions = [
        AssessmentQuestionResponse(
            id=q.id,
            question_text=q.question_text,
            options=json.loads(q.options) if q.options else []
        )
        for q in a.questions
    ]

    return AssessmentResponse(
        id=a.id,
        title=a.title,
        topic=a.topic,
        domain=a.domain,
        passing_percentage=a.passing_percentage,
        description=a.description or "",
        questions=questions
    )

@router.post("/{assessment_id}/submit", response_model=AssessmentSubmissionResult)
def submit_assessment(
    assessment_id: int,
    learner_id: int = Query(...),
    submission: AssessmentSubmissionRequest = None,
    db: Session = Depends(get_db)
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if not submission or not submission.answers:
        raise HTTPException(status_code=400, detail="Answers list is required")

    questions = a.questions
    total = len(questions)
    score = 0
    weak_areas = []
    question_results = []

    for idx, q in enumerate(questions):
        user_choice = submission.answers[idx] if idx < len(submission.answers) else -1
        is_correct = (user_choice == q.correct_option_index)
        if is_correct:
            score += 1
        else:
            weak_areas.append(f"{a.topic}: Concept in Q{idx + 1}")

        question_results.append(QuestionResultItem(
            question_id=q.id,
            question_text=q.question_text,
            selected_index=user_choice,
            correct_index=q.correct_option_index,
            is_correct=is_correct,
            explanation=q.explanation or ""
        ))

    percentage = round((score / total) * 100, 1) if total > 0 else 0.0
    passed = percentage >= a.passing_percentage

    attempt = LearnerAssessmentAttempt(
        learner_id=learner_id,
        assessment_id=a.id,
        score=score,
        total_questions=total,
        percentage=percentage,
        passed=passed,
        weak_areas=json.dumps(weak_areas),
        submitted_answers=json.dumps(submission.answers)
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Adaptive trigger
    adaptive_action = adapt_path_after_assessment(db, learner_id, attempt)

    # Check milestones
    update_and_check_milestones(db, learner_id)

    return AssessmentSubmissionResult(
        attempt_id=attempt.id,
        score=score,
        total_questions=total,
        percentage=percentage,
        passed=passed,
        weak_areas=weak_areas,
        question_results=question_results,
        adaptive_action=adaptive_action
    )
