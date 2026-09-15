import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Learner, LearnerFeedback, LearningPathItem, LearnerAssessmentAttempt, Assessment
from app.seed_data import seed_database
from app.services.recommendation_service import build_or_refresh_learning_path
from app.services.adaptive_service import adapt_path_after_feedback, adapt_path_after_assessment

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    seed_database(db)
    yield db
    db.close()

def test_adaptive_feedback_inserts_refresher(test_db):
    learner = Learner(
        name="Sam Student",
        target_goal="Become a Cloud Engineer",
        direction="Cloud / DevOps",
        current_knowledge=json.dumps([]),
        current_level="Beginner",
        available_time="1 hour daily",
        target_timeline="3 months"
    )
    test_db.add(learner)
    test_db.commit()

    path = build_or_refresh_learning_path(test_db, learner.id)
    initial_count = len(path.items)

    current_item = next(i for i in path.items if i.status == "in_progress")

    # Learner submits difficult feedback
    fb = LearnerFeedback(
        learner_id=learner.id,
        item_type="stage",
        item_id=current_item.id,
        item_title=current_item.title,
        rating="difficult",
        comment="I understand the theory but need more practice."
    )
    test_db.add(fb)
    test_db.commit()

    action = adapt_path_after_feedback(test_db, learner.id, fb)
    assert "practice module" in action.lower() or "inserted" in action.lower()

    # Verify new remedial item exists
    updated_items = test_db.query(LearningPathItem).filter(LearningPathItem.path_id == path.id).all()
    assert len(updated_items) == initial_count + 1
    remedial = next((i for i in updated_items if i.is_adaptive_remedial), None)
    assert remedial is not None
    assert "refresher" in remedial.title.lower() or "practice" in remedial.title.lower()

def test_adaptive_assessment_failure_inserts_remedial(test_db):
    learner = Learner(
        name="Jordan",
        target_goal="Full-Stack Web Dev",
        direction="Full-Stack Web",
        current_knowledge=json.dumps([]),
        current_level="Beginner"
    )
    test_db.add(learner)
    test_db.commit()

    path = build_or_refresh_learning_path(test_db, learner.id)
    assessment = test_db.query(Assessment).filter(Assessment.domain == "Full-Stack Web").first()

    # Attempt with failing score (e.g. 0/3)
    attempt = LearnerAssessmentAttempt(
        learner_id=learner.id,
        assessment_id=assessment.id,
        score=0,
        total_questions=3,
        percentage=0.0,
        passed=False,
        weak_areas=json.dumps([assessment.topic]),
        submitted_answers=json.dumps([1, 1, 1])
    )
    test_db.add(attempt)
    test_db.commit()

    action = adapt_path_after_assessment(test_db, learner.id, attempt)
    assert "refresher" in action.lower() or "weak" in action.lower()

    # Verify weak areas saved to learner profile
    test_db.refresh(learner)
    weaks = json.loads(learner.weak_areas)
    assert len(weaks) > 0
