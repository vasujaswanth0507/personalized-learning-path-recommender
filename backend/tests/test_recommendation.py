import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Learner, Skill, SkillPrerequisite, LearningPathItem
from app.seed_data import seed_database
from app.services.recommendation_service import build_or_refresh_learning_path

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    seed_database(db)
    yield db
    db.close()

def test_recommendation_prerequisite_skipping(test_db):
    """
    If learner already knows Linux, Linux should be credited/completed
    and the next eligible stage (Networking) should be unlocked.
    """
    learner = Learner(
        name="Jordan Cloud",
        target_goal="Become a Cloud Engineer",
        direction="Cloud / DevOps",
        current_knowledge=json.dumps(["Linux", "Python"]),
        current_level="Early Intermediate",
        available_time="1-2 hours daily",
        target_timeline="3 months"
    )
    test_db.add(learner)
    test_db.commit()
    test_db.refresh(learner)

    path = build_or_refresh_learning_path(test_db, learner.id)
    assert path is not None
    assert len(path.items) > 0

    # First item (Linux) should be marked as completed because learner knows it
    linux_item = next((i for i in path.items if "linux" in i.title.lower()), None)
    assert linux_item is not None
    assert linux_item.status == "completed"

    # Networking should be active (in_progress)
    net_item = next((i for i in path.items if "networking" in i.title.lower()), None)
    assert net_item is not None
    assert net_item.status == "in_progress"

    # Explanation should explicitly mention prior knowledge
    assert "familiarity" in linux_item.why_recommended.lower() or "completed" in linux_item.why_recommended.lower()
