import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.database import SessionLocal, Base, engine
from app.seed_data import seed_database

Base.metadata.create_all(bind=engine)
db = SessionLocal()
seed_database(db)
db.close()

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"

def test_onboarding_turn():
    payload = {
        "message": "I want to become a cloud engineer. I already know Linux and Python and have used EC2 once.",
        "history": [],
        "current_extracted": {}
    }
    res = client.post("/api/onboarding/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert data["is_ready_for_profile"] is True
    ext = data["extracted_profile"]
    assert "Cloud" in ext["direction"]
    assert "Linux" in ext["current_knowledge"] or "Linux Shell" in ext["current_knowledge"]

def test_create_profile_and_get_dashboard():
    # 1. Create learner
    profile_payload = {
        "name": "Jordan Cloud",
        "target_goal": "Cloud Solutions Architect",
        "direction": "Cloud / DevOps",
        "current_knowledge": ["Linux", "Basic AWS"],
        "current_level": "Early Intermediate",
        "available_time": "2 hours daily",
        "target_timeline": "3 months",
        "learning_preference": "Practical / Project-based",
        "weak_areas": [],
        "areas_to_explore": ["Terraform", "Kubernetes"],
        "notes": "Testing integration"
    }
    res = client.post("/api/profile", json=profile_payload)
    assert res.status_code == 200
    learner = res.json()
    learner_id = learner["id"]

    # 2. Get active path
    path_res = client.get(f"/api/paths/{learner_id}")
    assert path_res.status_code == 200
    path_data = path_res.json()
    assert len(path_data["items"]) > 0

    # 3. Get dashboard stats
    dash_res = client.get(f"/api/dashboard/{learner_id}")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["learner_name"] == "Jordan Cloud"
    assert "overall_progress_pct" in dash_data
    assert len(dash_data["skill_mastery"]) > 0
    assert len(dash_data["milestones"]) > 0

def test_reset_endpoint():
    # 1. Create a learner
    profile_payload = {
        "name": "Reset Test User",
        "target_goal": "Cloud Solutions Architect",
        "direction": "Cloud / DevOps",
        "current_knowledge": ["Linux"],
        "current_level": "Beginner",
        "available_time": "1 hour daily",
        "target_timeline": "3 months",
        "learning_preference": "Practical / Project-based",
        "weak_areas": [],
        "areas_to_explore": [],
        "notes": ""
    }
    res = client.post("/api/profile", json=profile_payload)
    assert res.status_code == 200
    learner = res.json()
    learner_id = learner["id"]

    # Verify learner exists in lists
    list_res = client.get("/api/profile")
    assert list_res.status_code == 200
    learners = list_res.json()
    assert any(l["id"] == learner_id for l in learners)

    # 2. Reset database
    reset_res = client.post("/api/profile/reset")
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert reset_data["status"] == "success"

    # 3. Verify learner list is now completely empty
    list_res2 = client.get("/api/profile")
    assert list_res2.status_code == 200
    assert len(list_res2.json()) == 0
