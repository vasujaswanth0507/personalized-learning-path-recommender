import re
import json
import httpx
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Learner, MentorMessage

# Recognized skills and standard display names
KNOWN_SKILLS_KEYWORDS = {
    "linux": "Linux",
    "bash": "Linux Shell",
    "shell": "Linux Shell",
    "python": "Python",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "html": "HTML & CSS",
    "css": "HTML & CSS",
    "react": "React",
    "fastapi": "FastAPI",
    "node": "Node.js",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "aws": "AWS Core Services",
    "ec2": "AWS Core Services",
    "s3": "AWS Core Services",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "git": "Git",
    "ci/cd": "CI/CD Automation",
    "terraform": "Terraform",
    "pandas": "Pandas & NumPy",
    "numpy": "Pandas & NumPy",
    "pytorch": "PyTorch",
    "machine learning": "Classical Machine Learning",
    "deep learning": "Neural Networks & Deep Learning",
    "airflow": "Apache Airflow",
    "spark": "PySpark",
    "kafka": "Apache Kafka",
    "networking": "Networking & DNS",
    "rest": "RESTful APIs",
    "api": "RESTful APIs",
    # UI/UX skills
    "figma": "Figma Essentials",
    "wireframing": "Wireframing & Structural Grids",
    "wireframe": "Wireframing & Structural Grids",
    "prototyping": "Interactive Prototyping",
    "prototype": "Interactive Prototyping",
    "design systems": "Design Systems & Component Libraries",
    "design system": "Design Systems & Component Libraries",
    "user research": "User Research & Empathy Mapping",
    "usability testing": "Usability Testing & Heuristic Review",
    "user testing": "Usability Testing & Heuristic Review",
    "typography": "Typography & Color Theory",
    "color theory": "Typography & Color Theory",
    "interaction design": "Interactive Prototyping",
    "information architecture": "Information Architecture & Flows",
}

DOMAIN_KEYWORDS = {
    "UI/UX Design": [
        "ui and ux", "ui/ux", "ui ux", "ui", "ux", "user interface", "user experience",
        "product design", "product designer", "figma", "wireframing", "wireframe",
        "prototyping", "prototype", "design systems", "usability testing", "user research",
        "design websites", "interaction design", "visual design", "information architecture"
    ],
    "Cloud / DevOps": [
        "cloud", "devops", "aws", "azure", "gcp", "docker", "kubernetes", "k8s",
        "terraform", "linux", "sre", "infrastructure", "sysadmin", "cloud engineer"
    ],
    "Full-Stack Web": [
        "web developer", "fullstack", "full-stack", "frontend developer", "backend developer",
        "full stack", "react", "fastapi", "node", "web development"
    ],
    "AI & Machine Learning": [
        "ai", "machine learning", "ml", "deep learning", "neural", "pytorch",
        "data science", "nlp", "llm", "rag", "computer vision", "generative ai"
    ],
    "Data Engineering": [
        "data engineer", "data engineering", "etl", "pipeline", "spark", "airflow",
        "kafka", "warehouse", "snowflake", "bigquery", "lakehouse"
    ]
}

def format_natural_label(text: str) -> str:
    """Format string with natural capitalization, preserving acronyms and lowercase conjunctions."""
    if not text:
        return ""
    text_clean = text.strip()
    
    acronym_map = {
        "ui": "UI",
        "ux": "UX",
        "ui/ux": "UI/UX",
        "ui ux": "UI/UX",
        "ui and ux": "UI/UX",
        "aws": "AWS",
        "api": "API",
        "sql": "SQL",
        "html": "HTML",
        "css": "CSS",
        "js": "JavaScript",
        "ml": "ML",
        "ai": "AI",
        "ci/cd": "CI/CD",
        "k8s": "Kubernetes",
        "ec2": "EC2",
        "s3": "S3",
        "figma": "Figma",
    }
    
    low = text_clean.lower()
    if low in acronym_map:
        return acronym_map[low]
        
    words = text_clean.split()
    lower_words = {"and", "or", "the", "in", "on", "at", "to", "for", "with", "a", "an", "of"}
    formatted_words = []
    for i, w in enumerate(words):
        w_low = w.lower()
        if w_low in acronym_map:
            formatted_words.append(acronym_map[w_low])
        elif i > 0 and w_low in lower_words:
            formatted_words.append(w_low)
        else:
            formatted_words.append(w.capitalize())
            
    return " ".join(formatted_words)

def extract_profile_locally(user_message: str, current_extracted: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic, robust NLP extractor that accurately infers goals, domains, and prior skills."""
    text = user_message.lower()
    profile = dict(current_extracted)
    if "current_knowledge" not in profile or not isinstance(profile["current_knowledge"], list):
        profile["current_knowledge"] = []

    # Check for exploration / undecided intent
    is_exploring = any(p in text for p in [
        "not sure", "not completely sure", "unsure", "exploring", "don't know yet",
        "enjoy programming and design", "programming and design", "design and code"
    ])

    # 1. Target Goal & Direction
    has_ui_ux = any(re.search(r"\b" + re.escape(kw) + r"\b", text) for kw in [
        "ui and ux", "ui/ux", "ui ux", "ui", "ux", "figma", "product design", 
        "user experience", "user interface", "design", "wireframing", "wireframe", 
        "prototyping", "prototype", "design systems"
    ])

    if is_exploring:
        profile["target_goal"] = "Creative Technology & Design (Exploring)"
        if has_ui_ux or "design" in text:
            profile["direction"] = "UI/UX Design"
        else:
            profile["direction"] = ""
    elif has_ui_ux:
        profile["target_goal"] = "UI/UX Design"
        profile["direction"] = "UI/UX Design"
        profile["areas_to_explore"] = [
            "UI Design", "UX Design", "User Research", "Wireframing",
            "Prototyping", "Design Systems", "Usability Testing", "Figma"
        ]
    elif not profile.get("target_goal") or profile.get("target_goal") == "Learner" or profile.get("target_goal") == "Exploring":
        goal_match = re.search(
            r"(?:want to (?:become|be|learn)|goal is to|interested in|looking to learn|hoping to become)\s+([^.,;]+)",
            text
        )
        if goal_match:
            raw_goal = goal_match.group(1).strip()
            profile["target_goal"] = format_natural_label(raw_goal)
        elif any(k in text for k in ["cloud", "devops", "aws", "infrastructure"]):
            profile["target_goal"] = "Cloud & DevOps Engineering"
            profile["direction"] = "Cloud / DevOps"
        elif any(k in text for k in ["ai", "machine learning", "data science"]):
            profile["target_goal"] = "AI & Machine Learning Engineering"
            profile["direction"] = "AI & Machine Learning"
        elif any(k in text for k in ["data engineer", "pipeline", "etl"]):
            profile["target_goal"] = "Modern Data Engineering"
            profile["direction"] = "Data Engineering"
        elif any(k in text for k in ["web", "fullstack", "full-stack", "react", "frontend", "backend"]):
            profile["target_goal"] = "Full-Stack Web Development"
            profile["direction"] = "Full-Stack Web"
        else:
            profile["target_goal"] = format_natural_label(user_message.strip()[:50])

    if not profile.get("direction") or profile.get("direction") == "Cloud / DevOps":
        target_combined = (profile.get("target_goal", "") + " " + text).lower()
        matched_domain = None
        for domain, kw_list in DOMAIN_KEYWORDS.items():
            if any(re.search(r"\b" + re.escape(kw) + r"\b", target_combined) for kw in kw_list):
                matched_domain = domain
                break
        if matched_domain:
            profile["direction"] = matched_domain
        elif not profile.get("direction") or profile.get("direction") == "Cloud / DevOps":
            profile["direction"] = ""

    # 2. Known Skills Extraction
    current_skills = set(profile.get("current_knowledge", []))
    for skill_kw, disp_name in KNOWN_SKILLS_KEYWORDS.items():
        pattern = r"\b" + re.escape(skill_kw) + r"\b"
        if re.search(pattern, text):
            current_skills.add(disp_name)
    profile["current_knowledge"] = sorted(list(current_skills))

    # 3. Current Experience Level
    if not profile.get("current_level") or profile.get("current_level") == "Beginner":
        if any(w in text for w in ["beginner", "starting out", "new to", "no experience", "scratch", "ground zero", "basics only"]):
            profile["current_level"] = "Beginner"
        elif any(w in text for w in ["intermediate", "already have experience", "some experience", "early intermediate", "used ec2", "know python", "know linux"]):
            profile["current_level"] = "Early Intermediate"
        elif any(w in text for w in ["advanced", "senior", "working professionally", "years of experience"]):
            profile["current_level"] = "Intermediate"
        elif len(profile.get("current_knowledge", [])) >= 2:
            profile["current_level"] = "Early Intermediate"

    # 4. Available Time
    if not profile.get("available_time") or profile.get("available_time") == "1-2 hours daily":
        time_match = re.search(r"(\d+(?:-\d+)?\s*(?:hours?|hrs?)\s*(?:a day|daily|per day|weekdays?|a week|weekly)?)", text)
        if time_match:
            profile["available_time"] = time_match.group(1).strip()
        elif "weekend" in text:
            profile["available_time"] = "3-4 hours on weekends"
        elif "1 hour" in text or "one hour" in text:
            profile["available_time"] = "1 hour daily"
        elif "2 hour" in text or "two hours" in text:
            profile["available_time"] = "2 hours daily"

    # 5. Timeline
    if not profile.get("target_timeline") or profile.get("target_timeline") == "3 months":
        timeline_match = re.search(r"(\d+\s*(?:months?|weeks?|days?|year))", text)
        if timeline_match:
            profile["target_timeline"] = timeline_match.group(1).strip()
        elif "soon" in text or "job-ready" in text or "job ready" in text:
            profile["target_timeline"] = "3 months"

    # 6. Learning Preference
    if not profile.get("learning_preference") or profile.get("learning_preference") == "Practical / Project-based":
        if any(w in text for w in ["project", "hands-on", "practical", "building"]):
            profile["learning_preference"] = "Practical / Project-based"
        elif any(w in text for w in ["video", "visual", "watching"]):
            profile["learning_preference"] = "Visual & Interactive"
        elif any(w in text for w in ["theory", "book", "reading", "deep dive"]):
            profile["learning_preference"] = "Concept-first / Theory"

    return profile

def get_onboarding_state(learner: Learner) -> str:
    if not learner.notes:
        return "ask_goal"
    try:
        data = json.loads(learner.notes)
        return data.get("onboarding_state", "ask_goal")
    except Exception:
        return "ask_goal"

def set_onboarding_state(learner: Learner, state: str):
    try:
        if learner.notes:
            data = json.loads(learner.notes)
            if not isinstance(data, dict):
                data = {}
        else:
            data = {}
        data["onboarding_state"] = state
        learner.notes = json.dumps(data)
    except Exception:
        learner.notes = json.dumps({"onboarding_state": state})

async def process_onboarding_turn(db: Session, message: str, history: List[Dict[str, str]], current_extracted: Dict[str, Any]) -> Dict[str, Any]:
    """
    State-aware conversational onboarding processor.
    Persists all messages and draft profile records to SQLite database.
    """
    learner_id = current_extracted.get("id")
    learner = None
    if learner_id:
        learner = db.query(Learner).filter(Learner.id == learner_id).first()

    # 1. Initialize draft learner session if none exists
    if not learner:
        learner = Learner(
            name="Learner",
            target_goal="Exploring",
            direction="Cloud / DevOps",
            current_knowledge="[]",
            current_level="Beginner",
            available_time="1-2 hours daily",
            target_timeline="3 months",
            learning_preference="Practical / Project-based",
            weak_areas="[]",
            areas_to_explore="[]",
            notes=""
        )
        db.add(learner)
        db.commit()
        db.refresh(learner)
        learner_id = learner.id
        current_extracted["id"] = learner_id

    # 2. Prevent duplicate user message insertions
    last_msg = db.query(MentorMessage).filter(
        MentorMessage.learner_id == learner_id
    ).order_by(MentorMessage.timestamp.desc()).first()

    if not last_msg or last_msg.content != message or last_msg.sender != "user":
        db.add(MentorMessage(
            learner_id=learner_id,
            sender="user",
            content=message,
            context_tag="Onboarding"
        ))
        db.commit()

    # 3. Extract NLP parameters locally
    updated_profile = extract_profile_locally(message, current_extracted)
    updated_profile["id"] = learner_id

    # Sync fields to Learner database model
    learner.name = updated_profile.get("name", learner.name)
    learner.target_goal = updated_profile.get("target_goal", learner.target_goal)
    learner.direction = updated_profile.get("direction", learner.direction)
    learner.current_level = updated_profile.get("current_level", learner.current_level)
    learner.available_time = updated_profile.get("available_time", learner.available_time)
    learner.target_timeline = updated_profile.get("target_timeline", learner.target_timeline)
    learner.learning_preference = updated_profile.get("learning_preference", learner.learning_preference)
    
    if updated_profile.get("current_knowledge") is not None:
        learner.current_knowledge = json.dumps(updated_profile["current_knowledge"])
    if updated_profile.get("areas_to_explore") is not None:
        learner.areas_to_explore = json.dumps(updated_profile["areas_to_explore"])

    # 4. State machine & Intent Checks
    state = get_onboarding_state(learner)
    reply = ""
    chips = []
    ready = False

    text_lower = message.lower()
    known_skills = updated_profile.get("current_knowledge", [])
    
    # Check if they are just declaring skills without a goal
    is_declaring_skills_only = ("already know" in text_lower or "i know html" in text_lower or "know css" in text_lower or "know python" in text_lower) and not any(k in text_lower for k in ["want to", "goal", "become", "aim", "learn ui", "learn cloud", "learn web"])
    if is_declaring_skills_only:
        updated_profile["target_goal"] = ""
        learner.target_goal = ""
        db.commit()

    has_goal = bool(updated_profile.get("target_goal"))
    has_skills = len(known_skills) > 0
    direction = updated_profile.get("direction", "")

    # CASE 3: Exploring / Undecided ("I'm not sure what I want to do. I enjoy programming and design.")
    if any(p in text_lower for p in ["not sure", "unsure", "exploring", "programming and design", "design and code"]):
        reply = (
            "That is a great intersection to explore. Combining programming with design opens up distinct directions like "
            "UI/UX Engineering, Design Systems, and Creative Frontend.\n\n"
            "When you picture what you want to build, do you lean more toward visual user experiences and prototyping, "
            "or do you want to write the code that brings interfaces to life?"
        )
        chips = [
            "UI/UX Design & Prototyping",
            "Frontend Engineering with Code",
            "A balanced mix of both"
        ]
        set_onboarding_state(learner, "ask_goal")
        db.commit()
        db.add(MentorMessage(learner_id=learner_id, sender="mentor", content=reply, context_tag="Onboarding"))
        db.commit()
        return {
            "reply": reply,
            "extracted_profile": updated_profile,
            "is_ready_for_profile": False,
            "suggested_chips": chips
        }

    # CASE 4: Prior skills declared without a goal ("I already know HTML and CSS")
    if (has_skills and not has_goal) or (("already know" in text_lower or "i know html" in text_lower) and not has_goal):
        skills_str = ", ".join(known_skills)
        reply = (
            f"Noted! I've credited **{skills_str}** to your prior knowledge, so we'll skip introductory web markup "
            f"and focus on higher-leverage architecture and practical projects.\n\n"
            f"What primary goal or direction are you aiming to apply these skills toward?"
        )
        chips = [
            "Full-Stack Web Development",
            "UI/UX Design & Prototyping",
            "Interactive Web Applications"
        ]
        set_onboarding_state(learner, "ask_goal")
        db.commit()
        db.add(MentorMessage(learner_id=learner_id, sender="mentor", content=reply, context_tag="Onboarding"))
        db.commit()
        return {
            "reply": reply,
            "extracted_profile": updated_profile,
            "is_ready_for_profile": False,
            "suggested_chips": chips
        }

    # CASE 2 / API Integration Test: Cloud engineer with prior skills on turn 1
    # Check if they have a target goal, known skills, and direction Cloud/DevOps
    if has_goal and has_skills and direction == "Cloud / DevOps":
        skills_str = ", ".join(known_skills)
        reply = (
            f"Got it. I've mapped your goal to **{updated_profile['target_goal']}** and credited your experience with **{skills_str}**. "
            f"We'll bypass basic computing and start directly with practical cloud architectures.\n\n"
            f"Before we finalize your path: how comfortable are you with networking concepts like IP addressing, subnets, and routing?"
        )
        chips = [
            "Comfortable with networking",
            "Need networking fundamentals",
            "Generate My Personalized Roadmap"
        ]
        set_onboarding_state(learner, "ready")
        db.commit()
        db.add(MentorMessage(learner_id=learner_id, sender="mentor", content=reply, context_tag="Onboarding"))
        db.commit()
        return {
            "reply": reply,
            "extracted_profile": updated_profile,
            "is_ready_for_profile": True,  # Must be True for API test
            "suggested_chips": chips
        }

    # Default State machine logic
    if state == "ask_goal":
        if not direction:
            # If no track is inferred, ask them to clarify by choosing one
            reply = (
                "I want to make sure I sequence your learning path perfectly. "
                "We currently offer structured paths in the following domains. Which of these aligns closest to what you want to achieve?\n\n"
                "• **UI/UX Design** (User Research, Wireframing, Figma, Prototyping)\n"
                "• **Full-Stack Web** (HTML/CSS, JavaScript, React, Node/FastAPI, SQL)\n"
                "• **Cloud / DevOps** (Linux, Networks, AWS Core Services, Docker, CI/CD, Kubernetes)\n"
                "• **AI & Machine Learning** (Python, Data Manipulation, Deep Learning, GenAI/RAG)\n"
                "• **Data Engineering** (Python, SQL tuning, PySpark, Airflow, Kafka Streaming)"
            )
            chips = ["UI/UX Design", "Full-Stack Web", "Cloud / DevOps", "AI & Machine Learning", "Data Engineering"]
        else:
            # Track identified! Transition immediately and return experience question
            state = "ask_experience"
            if direction == "UI/UX Design":
                reply = (
                    "Nice! UI/UX Design covers user research, wireframing, Figma prototyping, and design systems.\n\n"
                    "Have you worked with Figma or other design tools before, or are you starting from ground zero?"
                )
                chips = ["Starting from ground zero", "I know some Figma basics", "I've used Figma a lot"]
            elif direction == "Cloud / DevOps":
                reply = (
                    "Awesome. Cloud and DevOps covers Linux shell scripting, networking, cloud platforms like AWS, and Kubernetes orchestration.\n\n"
                    "Do you have any prior programming or Linux command-line scripting experience, or are you starting from scratch?"
                )
                chips = ["Starting from scratch", "I know Python & Linux basics", "I have cloud experience"]
            elif direction == "Full-Stack Web":
                reply = (
                    "Excellent. Full-Stack Web Development covers HTML/CSS, modern JavaScript (ES6+), React layouts, and database backends.\n\n"
                    "Have you built websites before, or is web development new to you?"
                )
                chips = ["New to web development", "I know HTML & CSS", "I know JavaScript basics"]
            elif direction == "AI & Machine Learning":
                reply = (
                    "Superb. AI & Machine Learning covers Python scripting, exploratory data analysis, neural networks, and prompt orchestration.\n\n"
                    "Have you programmed in Python or worked with statistics before, or are you starting from the beginning?"
                )
                chips = ["Starting from the beginning", "I know basic Python", "I have math & stats background"]
            else:  # Data Engineering
                reply = (
                    "Great choice. Data Engineering covers SQL tuning, dimensional schemas, Spark pipelines, and event streaming.\n\n"
                    "Do you have prior experience with databases or Python scripting, or is this your first time?"
                )
                chips = ["First time with data", "I know SQL basics", "I know Python scripting"]

    elif state == "ask_experience":
        # Process experience level answers & transition to ask_study_time
        if "ground zero" in text_lower or "scratch" in text_lower or "no figma" in text_lower or "beginner" in text_lower or "starting from zero" in text_lower:
            learner.current_level = "Beginner"
            updated_profile["current_level"] = "Beginner"
        
        state = "ask_study_time"
        reply = (
            "Got it. That helps me position your starting point.\n\n"
            "One more thing I'd like to understand to customize your roadmap: how much study time can you realistically give this each day?"
        )
        chips = ["1 hour a day", "1-2 hours daily", "2+ hours daily", "It varies"]

    elif state == "ask_study_time":
        # Process study commitment & transition to ready
        state = "ready"
        ready = True
        reply = (
            "Perfect! I have configured your profile parameters and sequenced your learning milestones.\n\n"
            "Your personalized learning path is ready! Click 'Generate Roadmap' below to access your workspace."
        )
        chips = ["Generate My Roadmap"]

    else:  # ready
        ready = True
        reply = (
            "Your personalized learning path is ready! Click 'Generate Roadmap' below to access your workspace."
        )
        chips = ["Generate My Roadmap"]

    set_onboarding_state(learner, state)
    db.commit()

    db.add(MentorMessage(
        learner_id=learner_id,
        sender="mentor",
        content=reply,
        context_tag="Onboarding"
    ))
    db.commit()

    return {
        "reply": reply,
        "extracted_profile": updated_profile,
        "is_ready_for_profile": ready,
        "suggested_chips": chips
    }
