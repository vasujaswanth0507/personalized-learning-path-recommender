# User Workflow & Journey: LearnPath

```mermaid
sequenceDiagram
    autonumber
    actor Learner
    participant UI as Web Frontend (React)
    participant API as FastAPI Backend
    participant Engine as Recommendation & Adaptive Engine
    participant DB as SQLite DB
    participant AI as AI Mentor (Gemini / Local)

    Learner->>UI: Opens LearnPath
    UI->>Learner: Welcomes warmly with natural onboarding prompt
    Learner->>UI: Types background: "I want to become a cloud engineer. I know Linux and Python..."
    UI->>API: POST /api/onboarding/chat
    API->>AI: Extracts goal, skills, level, timeline
    API-->>UI: Returns profile preview and confirmation
    Learner->>UI: Clicks "Generate Personalized Learning Roadmap"
    UI->>API: POST /api/profile
    API->>Engine: build_or_refresh_learning_path()
    Engine->>DB: Resolves DAG prerequisites & credits Linux
    Engine-->>DB: Stores personalized path with explanations
    API-->>UI: Returns Learner + Path
    UI->>Learner: Displays Dashboard with real progress & active stage (Networking)
    
    Learner->>UI: Explores Recommended Resources
    Learner->>UI: Marks resource as Completed
    UI->>API: POST /api/resources/{id}/progress
    API->>DB: Saves completion, recalculates metrics
    
    Learner->>UI: Takes Topic Assessment Quiz
    UI->>API: POST /api/assessments/{id}/submit
    API->>Engine: Evaluates answers
    alt Passed (>= 70%)
        Engine->>DB: Unlocks next stage & awards milestone
    else Score < 70%
        Engine->>DB: Logs weak area & inserts Refresher Stage
    end
    API-->>UI: Renders score, explanations, and adaptive update

    Learner->>UI: Submits Feedback: "Need more hands-on practice"
    UI->>API: POST /api/feedback
    API->>Engine: adapt_path_after_feedback()
    Engine-->>DB: Injects guided practice module into roadmap

    Learner->>UI: Clicks "AI Mentor" button
    UI->>Learner: Opens drawer with active stage context
    Learner->>UI: "Why am I learning networking before AWS?"
    UI->>API: POST /api/mentor/{id}/chat
    API->>AI: Synthesizes pedagogical answer using learner's path
    AI-->>UI: Returns explanation grounded in learner's real progress
```

## Step-by-Step Experience

1. **Conversational Onboarding**:
   - The learner enters goals and existing knowledge naturally.
   - The system avoids redundant questions, extracting level, timeline, and preferences automatically.
2. **Review & Calibration**:
   - The live profile preview displays what the system inferred.
   - The learner can correct or expand their prior skills before generating the roadmap.
3. **Personalized Roadmap Exploration**:
   - The generated roadmap credits prior knowledge (e.g. Linux) and unlocks eligible modules.
   - Every stage features an explicit "Why this recommendation?" box.
4. **Active Learning & Progress**:
   - The learner marks resources as in progress or completed.
   - The dashboard updates mathematically from actual database records.
5. **Interactive Quizzes**:
   - Quizzes validate comprehension and provide immediate answer explanations.
   - Scores below 70% automatically adapt the roadmap by scheduling a refresher module.
6. **Adaptive Feedback Loop**:
   - Quick ratings ("Easy", "Difficult") and free-text notes dynamically adapt subsequent recommendations.
7. **Always-Available AI Mentor**:
   - The mentor drawer maintains awareness of the learner's current stage, completed topics, weak areas, and time constraints.
