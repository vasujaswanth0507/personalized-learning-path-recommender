import json
import httpx
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.config import settings
from app.models import (
    Learner, LearningPath, LearningPathItem, LearnerFeedback,
    LearnerAssessmentAttempt, MentorMessage
)

async def ask_ai_mentor(
    db: Session,
    learner_id: int,
    user_message: str,
    current_stage: str = "",
    context_topic: str = ""
) -> Dict[str, Any]:
    """
    Context-aware AI Mentor that uses learner profile, active roadmap stages,
    completed topics, feedback, and weak areas.
    Uses Gemini API when configured (with full conversation memory), 
    and a robust intent-aware local fallback.
    """
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        return {"reply": "Learner profile not found.", "suggested_followups": []}

    # Gather real context
    path = db.query(LearningPath).filter(
        LearningPath.learner_id == learner_id,
        LearningPath.is_active == True
    ).first()

    completed_stages = []
    current_item = None
    all_stages = []

    if path:
        items = db.query(LearningPathItem).filter(
            LearningPathItem.path_id == path.id
        ).order_by(LearningPathItem.stage_order).all()
        for i in items:
            all_stages.append(i.title)
            if i.status == "completed":
                completed_stages.append(i.title)
            elif i.status == "in_progress" and not current_item:
                current_item = i.title

    active_stage_name = current_stage or current_item or (all_stages[0] if all_stages else "Foundations")
    weak_areas = json.loads(learner.weak_areas) if learner.weak_areas else []
    known_skills = json.loads(learner.current_knowledge) if learner.current_knowledge else []

    # Store user message in database history
    db.add(MentorMessage(
        learner_id=learner_id,
        sender="user",
        content=user_message,
        context_tag=active_stage_name
    ))
    db.commit()

    # Query last 10 messages of history (reversed for chronological order)
    history_messages = db.query(MentorMessage).filter(
        MentorMessage.learner_id == learner_id
    ).order_by(MentorMessage.timestamp.desc()).limit(10).all()
    history_messages = list(reversed(history_messages))

    reply_text = ""
    followups = []

    # 1. Attempt Gemini Call with conversation history
    if settings.GEMINI_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                system_prompt = (
                    f"You are the personalized learning mentor for {learner.name} on LearnPath.\n"
                    f"Learner Context:\n"
                    f"- Goal: {learner.target_goal} ({learner.direction})\n"
                    f"- Skill Level: {learner.current_level}\n"
                    f"- Time Budget: {learner.available_time}\n"
                    f"- Learning Preference: {learner.learning_preference}\n"
                    f"- Prior Known Skills: {', '.join(known_skills)}\n"
                    f"- Completed Stages: {', '.join(completed_stages) if completed_stages else 'None yet'}\n"
                    f"- Currently Active Stage: {active_stage_name}\n"
                    f"- Identified Weak Areas: {', '.join(weak_areas) if weak_areas else 'None'}\n\n"
                    "INSTRUCTIONS:\n"
                    "- Provide concise, encouraging, concrete advice grounded strictly in this learner's roadmap.\n"
                    "- Do not start responses with generic intro phrases like 'I'm here to help' or 'Great question'. Ask questions or give tips directly.\n"
                    "- If they ask why a topic is recommended or sequenced, explain the prerequisite dependency.\n"
                    "- If they say they already know something, explain how they can skip or fast-track it.\n"
                    "- Output strictly JSON with keys: 'reply' (markdown string) and 'suggested_followups' (list of 2-3 short strings)."
                )
                
                # Format contents for Gemini turn-by-turn API
                contents = []
                for msg in history_messages:
                    contents.append({
                        "role": "user" if msg.sender == "user" else "model",
                        "parts": [{"text": msg.content}]
                    })

                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": contents,
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "generationConfig": {"response_mime_type": "application/json"}
                }
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidate = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(candidate)
                    reply_text = parsed.get("reply", "")
                    followups = parsed.get("suggested_followups", [])
        except Exception as e:
            print(f"Gemini mentor fallback triggered: {e}")

    # 2. Resilient Context-Aware Local Fallback
    if not reply_text:
        msg_lower = user_message.lower()

        # A: Recommendation Reasoning ("Why is this recommended?" / "Why am I learning X before Y?")
        if "why" in msg_lower or "recommend" in msg_lower or "sequence" in msg_lower or "order" in msg_lower:
            reply_text = (
                f"Great question! **{active_stage_name}** is sequenced on your roadmap for your goal of **{learner.target_goal}** "
                f"because it serves as a critical step. In the **{learner.direction}** path, understanding these concepts is necessary "
                f"before moving on to more complex tools. Completing this stage helps you build the foundational knowledge "
                f"required for subsequent advanced steps."
            )
            followups = ["Can I take the assessment now?", "What should I study today?"]

        # B: Study Planning ("What should I study today?")
        elif "what should i study" in msg_lower or "study plan" in msg_lower or "today" in msg_lower:
            reply_text = (
                f"Based on your daily target of **{learner.available_time}**, here is a focused plan for today:\n\n"
                f"1. **Core Concept (20-30 mins)**: Spend the first block reviewing the main reference material for **{active_stage_name}**.\n"
                f"2. **Hands-on practice (20-30 mins)**: Recreate a small task, type out commands, or sketch layout structures locally.\n"
                f"3. **Recap (10 mins)**: Write down the top 3 takeaways or take the assessment to test your retention."
            )
            followups = ["Open curated resources", "Explain this topic simply"]

        # C: Concept explanation ("Explain User Research simply" / "What is a wireframe?")
        elif "explain" in msg_lower or "what is" in msg_lower or "definition" in msg_lower or "concept" in msg_lower or "wireframe" in msg_lower or "research" in msg_lower:
            reply_text = (
                f"Let's break down **{active_stage_name}** simply:\n\n"
                f"Think of it like laying the blueprints before starting construction. Instead of jumping straight into coding or designing, "
                f"this stage teaches you the fundamental rules and practices (like user wireframes or Linux command lines) that "
                f"prevent expensive mistakes later on. In **{learner.direction}**, every real-world project builds on this core knowledge."
            )
            followups = ["Give me a practice exercise", "What comes after this?"]

        # D: Difficulty/Help ("I don't understand this" / "I am struggling")
        elif "difficult" in msg_lower or "struggling" in msg_lower or "hard" in msg_lower or "don't understand" in msg_lower or "stuck" in msg_lower:
            reply_text = (
                f"Hitting friction is a normal part of the learning process, especially with **{active_stage_name}**.\n\n"
                f"To help move past this: \n"
                f"- Break down the current topic into smaller chunks.\n"
                f"- Submit feedback rating this stage as **Difficult** so LearnPath can dynamically insert a guided practice lab for you.\n"
                f"- Which part feels most confusing: the conceptual theory, or applying it in a practical exercise?"
            )
            followups = ["Explain this topic simply", "How do I trigger an adaptation?"]

        # E: Skip/Prerequisite ("Can I skip this topic?" / "I already know HTML")
        elif "skip" in msg_lower or "already know" in msg_lower or "fast-track" in msg_lower:
            reply_text = (
                f"Yes, you can absolutely bypass **{active_stage_name}** if you already understand these concepts.\n\n"
                f"Go to the **My Roadmap** page and click **Mark as Completed** or pass the assessment. "
                f"This will immediately credit the stage to your profile and unlock downstream modules."
            )
            followups = ["Take the assessment now", "View my roadmap"]

        # F: Time Constraint ("I only have 30 minutes today" / "I only have 15 minutes today")
        elif "30 minutes" in msg_lower or "15 minutes" in msg_lower or "time limit" in msg_lower or "short time" in msg_lower:
            reply_text = (
                f"With a shorter block of time today, let's execute a quick study sprint for **{active_stage_name}**:\n\n"
                f"- **Minutes 1-10**: Read the introduction or key takeaways of the recommended resource.\n"
                f"- **Minutes 11-25**: Do one small practical task (run 3 commands, review a persona, or read 1 block of code).\n"
                f"- **Minutes 26-30**: Log your notes and write a 1-sentence summary of what you reviewed."
            )
            followups = ["Open quick resource", "Ask me a simple review question"]

        # G: Progress ("How much progress have I made?" / "How far have I completed?")
        elif "progress" in msg_lower or "completed" in msg_lower or "how far" in msg_lower or "how much" in msg_lower:
            total = len(all_stages)
            done = len(completed_stages)
            pct = int((done / total) * 100) if total > 0 else 0
            reply_text = (
                f"You have completed **{done}** of **{total}** stages along your roadmap (**{pct}%** completion).\n\n"
                f"Your active target is **{active_stage_name}**. "
                f"Keep pushing forward—solidifying this stage brings you one step closer to your goal of **{learner.target_goal}**!"
            )
            followups = ["What should I study today?", "What comes after this?"]

        # H: Roadmap ("What comes after this?")
        elif "what comes after" in msg_lower or "next" in msg_lower or "roadmap" in msg_lower or "future" in msg_lower:
            next_stages = []
            found_active = False
            for s in all_stages:
                if found_active:
                    next_stages.append(s)
                if s == active_stage_name:
                    found_active = True
            
            next_str = ", ".join(next_stages[:2]) if next_stages else "none (this is the final leg of your journey!)"
            reply_text = (
                f"You are currently working on **{active_stage_name}**.\n\n"
                f"The next stages scheduled on your roadmap are: **{next_str}**. "
                f"Once you complete the current stage, the next ones will automatically unlock."
            )
            followups = ["What should I study today?", "Why is this recommended?"]

        # I: Resource ("Give me something easier" / "Give me a resource")
        elif "resource" in msg_lower or "easier" in msg_lower or "reference" in msg_lower or "reading" in msg_lower:
            reply_text = (
                f"To help with **{active_stage_name}**, check out the **Resources** tab in your workspace.\n\n"
                f"I have selected structured readings, interactive labs, and official documentation matching your "
                f"preference for **{learner.learning_preference}**. Starting with the shorter tutorials is usually easiest."
            )
            followups = ["View resources page", "Explain this topic simply"]

        # J: Learning Strategy ("How should I practice this?")
        elif "practice" in msg_lower or "strategy" in msg_lower or "learn" in msg_lower:
            reply_text = (
                f"To master **{active_stage_name}** effectively, I recommend an active strategy:\n\n"
                f"- **Recreation**: Try to recreate examples from scratch without looking at the reference code/design.\n"
                f"- **Small Steps**: Build extremely simple tests (e.g. wireframe a single button, or run one curl command).\n"
                f"- **Recall**: Explain the core concept aloud or write it down in your notes file."
            )
            followups = ["What project should I build?", "Give me a simple exercise"]

        # K: Project ("What should I build after learning this?")
        elif "build" in msg_lower or "project" in msg_lower or "portfolio" in msg_lower:
            reply_text = (
                f"To apply what you learn in **{active_stage_name}**, navigate to the **Projects** tab.\n\n"
                f"You will find hands-on, objective-based projects styled for your goal of **{learner.target_goal}**. "
                f"Building these will give you practical portfolio deliverables to demonstrate your skills."
            )
            followups = ["Go to projects tab", "What should I study today?"]

        # L: Goal Change ("I want to focus more on UX than UI" / "Change goal")
        elif "goal change" in msg_lower or "change goal" in msg_lower or "focus more" in msg_lower or "direction" in msg_lower or "career" in msg_lower:
            reply_text = (
                f"No problem! Your learning journey should adapt as your goals evolve. \n\n"
                f"You can update your direction or goal at any time. Go to the **Profile** page, "
                f"click **Edit Profile**, make your adjustments, and select **Save & Recalculate** "
                f"to instantly align your roadmap with your new direction."
            )
            followups = ["Go to profile page", "Explain the active stage"]

        # M: Feedback ("This topic is too difficult" / "Feedback")
        elif "feedback" in msg_lower or "too difficult" in msg_lower:
            reply_text = (
                f"Thank you for sharing your feedback on **{active_stage_name}**.\n\n"
                f"If you are finding it difficult, click the **Feedback** action button on the stage in your roadmap "
                f"and submit a rating. LearnPath will adaptively modify your sequence by inserting helper refreshers."
            )
            followups = ["Take assessment to test my skills", "Explain this topic simply"]

        # N: General fallback (Dynamic based on current stage)
        else:
            reply_text = (
                f"I'm here to support you as your learning mentor on LearnPath!\n\n"
                f"You are currently focusing on **{active_stage_name}** as part of your **{learner.direction}** roadmap.\n"
                f"What would be most helpful right now? I can explain this topic simply, provide a timed study plan, "
                f"discuss why this is recommended, or help you fast-track it."
            )
            followups = ["What should I study today?", "Why is this recommended?", "Explain this topic simply"]

    # Store mentor reply in database history
    db.add(MentorMessage(
        learner_id=learner_id,
        sender="mentor",
        content=reply_text,
        context_tag=active_stage_name
    ))
    db.commit()

    return {
        "reply": reply_text,
        "suggested_followups": followups
    }
