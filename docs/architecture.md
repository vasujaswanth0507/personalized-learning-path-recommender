# Architecture Overview: LearnPath

## 1. System Architecture

**LearnPath** is architected as a modular, decoupled full-stack application with clean separation between user interface, business logic, recommendation algorithms, persistence, and AI orchestration.

```mermaid
graph TD
    User([Learner Browser])
    
    subgraph Frontend ["Frontend (React + Vite)"]
        UI_Nav[Navigation & Router]
        UI_Onboarding[Conversational Onboarding]
        UI_Dashboard[Progress Dashboard]
        UI_Roadmap[Interactive Learning Path]
        UI_Resources[Curated Resources Catalog]
        UI_Projects[Practical Projects Hub]
        UI_Assessments[Topic Assessments Engine]
        UI_Mentor[Context-Aware AI Mentor Drawer]
        UI_Feedback[Dynamic Feedback Modal]
        Context[Learner State Context]
    end

    subgraph Backend ["Backend (FastAPI REST API)"]
        API_Gateway[FastAPI Endpoints]
        
        subgraph Services ["Core Engine Services"]
            S_Onboarding[Onboarding & Extraction Service]
            S_Rec[Prerequisite & Recommendation Engine]
            S_Adapt[Adaptive Learning Service]
            S_Progress[Real Statistical Progress Calculator]
            S_Mentor[Contextual AI Mentor Service]
        end
        
        subgraph AI_Layer ["AI & Hybrid Intelligence"]
            Gemini_API["Google Gemini API (gemini-1.5-flash)"]
            Local_NLP["Deterministic Local NLP & Pedagogical Engine"]
        end
        
        subgraph Data_Layer ["Persistence (SQLAlchemy + SQLite)"]
            DB_Learners[(Learner Profiles)]
            DB_Skills[(Skills & Prerequisites DAG)]
            DB_Paths[(Learning Paths & Items)]
            DB_Resources[(Learning Resources)]
            DB_Projects[(Projects & Progress)]
            DB_Assessments[(Assessments & Attempts)]
            DB_Feedback[(Learner Feedback)]
            DB_Milestones[(Milestones & Unlocks)]
            DB_Chats[(Mentor Conversation Logs)]
        end
    end

    User <--> Frontend
    Frontend <--> |JSON / REST /api| API_Gateway
    API_Gateway --> Services
    S_Onboarding --> AI_Layer
    S_Mentor --> AI_Layer
    Services --> Data_Layer
```

## 2. Key Components

### 2.1 Frontend Architecture
- **Framework**: React 19 with Vite 8.
- **Styling**: Tailored, accessible Vanilla CSS design system based on Inter typography, consistent spacing tokens, cards, and smooth micro-interactions.
- **State Management**: Centralized `LearnerContext` managing active learner profile, dashboard statistics, toast alerts, global AI mentor drawer, and feedback modal.
- **Zero Mock Policy**: Every interactive control (status toggles, quiz submissions, profile updates, feedback forms, mentor queries) triggers authentic HTTP requests that mutate SQLite.

### 2.2 Backend Architecture
- **Framework**: Python 3.13 + FastAPI.
- **Data Persistence**: SQLAlchemy ORM with SQLite, ensuring zero complex database setup while providing ACID transactions and relational constraints.
- **Startup Seeding**: Automatically initializes tables and populates a rich 40-skill knowledge graph, realistic learning resources, projects, assessments, and milestones on first launch.

### 2.3 AI & Heuristic Layer
- **Primary LLM**: Google Gemini API (`gemini-1.5-flash`).
- **Resilient Local Fallback**: When `GEMINI_API_KEY` is not present in `.env` or during network interruptions, the application activates its deterministic local NLP and pedagogical advice engine. The app is **100% functional offline and without an API key**.
