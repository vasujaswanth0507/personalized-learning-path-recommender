from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_case_1_ui_ux_goal():
    """CASE 1: 'I want to learn UI and UX' must NOT become Full-Stack Web."""
    res = client.post("/api/onboarding/chat", json={
        "message": "I want to learn UI and UX",
        "history": [],
        "current_extracted": {}
    })
    assert res.status_code == 200
    data = res.json()
    ext = data["extracted_profile"]
    assert ext["direction"] == "UI/UX Design", f"Expected UI/UX Design but got {ext['direction']}"
    assert "UI" in ext["target_goal"] and "UX" in ext["target_goal"]
    assert ext["direction"] != "Full-Stack Web"
    # Ensure areas to explore contains UI/UX topics
    assert "areas_to_explore" in ext
    assert "Figma" in ext["areas_to_explore"]

def test_case_2_cloud_engineer_with_prior_skills():
    """CASE 2: 'I want to become a cloud engineer. I know Linux and Python.'"""
    res = client.post("/api/onboarding/chat", json={
        "message": "I want to become a cloud engineer. I know Linux and Python.",
        "history": [],
        "current_extracted": {}
    })
    assert res.status_code == 200
    data = res.json()
    ext = data["extracted_profile"]
    assert ext["direction"] == "Cloud / DevOps"
    assert "Linux" in ext["current_knowledge"]
    assert "Python" in ext["current_knowledge"]
    # The mentor should not ask what goal or skills they have
    reply = data["reply"]
    assert "what is your goal" not in reply.lower()
    assert "what skills do you know" not in reply.lower()
    assert "networking" in reply.lower()

def test_case_3_exploring_undecided():
    """CASE 3: 'I'm not sure what I want to do. I enjoy programming and design.'"""
    res = client.post("/api/onboarding/chat", json={
        "message": "I'm not sure what I want to do. I enjoy programming and design.",
        "history": [],
        "current_extracted": {}
    })
    assert res.status_code == 200
    data = res.json()
    reply = data["reply"].lower()
    # Mentor should explore options rather than forcing rigid domain
    assert "explore" in reply or "intersection" in reply or "bridging" in reply
    assert data["is_ready_for_profile"] is False

def test_case_4_prior_html_css_credited():
    """CASE 4: 'I already know HTML and CSS.'"""
    res = client.post("/api/onboarding/chat", json={
        "message": "I already know HTML and CSS.",
        "history": [],
        "current_extracted": {}
    })
    assert res.status_code == 200
    data = res.json()
    ext = data["extracted_profile"]
    assert "HTML & CSS" in ext["current_knowledge"]
    reply = data["reply"].lower()
    assert "skip" in reply or "credited" in reply

def test_ui_ux_roadmap_creation():
    """Verify that creating a profile with UI/UX Design generates a valid roadmap."""
    profile_payload = {
        "name": "Jordan Designer",
        "target_goal": "UI/UX Design",
        "direction": "UI/UX Design",
        "current_knowledge": ["HTML & CSS"],
        "current_level": "Beginner",
        "available_time": "1-2 hours daily",
        "target_timeline": "3 months",
        "learning_preference": "Practical / Project-based",
        "weak_areas": [],
        "areas_to_explore": ["Figma", "Design Systems"],
        "notes": ""
    }
    create_res = client.post("/api/profile", json=profile_payload)
    assert create_res.status_code == 200
    learner = create_res.json()
    assert learner["direction"] == "UI/UX Design"
    
    # Check that learning path was generated
    path_res = client.get(f"/api/paths/{learner['id']}")
    assert path_res.status_code == 200
    path = path_res.json()
    assert path["domain"] == "UI/UX Design"
    assert len(path["items"]) > 0
    # The first skill should be User Research or Wireframing
    skill_names = [item["title"] for item in path["items"]]
    assert any("Research" in s or "Wireframing" in s or "Figma" in s for s in skill_names)
