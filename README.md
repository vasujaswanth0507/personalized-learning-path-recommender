# LearnPath: Personalized Learning Workspace

LearnPath is an interactive learning platform that replaces generic, linear course catalogs with personalized, prerequisite-aware learning paths. By analyzing goals, prior experiences, and current skill sets through conversational onboarding, LearnPath constructs a tailored educational roadmap. As learners progress, the system continually evaluates understanding via assessments and feedback loops, dynamically inserting remedial content or fast-tracking topics to guarantee an optimal learning velocity.

---

## 1. Key Features
* **Conversational Onboarding**: Natural language onboarding chat with dynamic profile parameter extraction.
* **Prerequisite DAG Roadmap**: Visual stages mapped to skill dependency constraints (Completed, In Progress, Available, Locked).
* **Dynamic Path Adaptation**: Automatically injects remedial refreshers when learners fail quizzes or submit difficult feedback ratings.
* **Context-Aware Mentorship**: An integrated Mentor panel preloaded with stage context to answer concept questions, adjust study pacing, or provide scheduling suggestions.
* **Light and Dark Themes**: Elegant, high-contrast visual themes switchable globally and persisted across sessions.
* **LearnPath Startup Animation**: Sleek, polished logo reveal displayed on application initialization.
* **Danger Zone Data Deletion**: Full cascading database deletion that completely clears learner profiles, roadmaps, and chat history.

---

## 2. Technology Stack
* **Frontend**: React 19, Vite 8, SPA Page Routing, Vanilla CSS Design System, Local Storage Persistence.
* **Backend**: Python 3.13, FastAPI (Uvicorn gateway).
* **Database**: SQLite, SQLAlchemy ORM with cascade delete constraints.
* **Testing**: `pytest` test suite.

---

## 3. Folder Structure
```
HCL/
├── README.md                           # Main setup & execution guide
├── docs/                               # Project technical reports
│   ├── LearnPath_Solution_Documentation.md  # Primary technical solution report
│   ├── architecture.md                 # Architecture structure overview
│   ├── user_workflow.md                # Learner journey & onboarding states
│   ├── recommendation_logic.md         # Topological sorting & DAG DAG description
│   ├── data_model.md                   # SQLite schema mappings
│   └── testing.md                      # Pytest & Manual verification guide
├── backend/                            # FastAPI app, databases, routes, schemas
│   ├── app/
│   │   ├── main.py                     # API app gateway
│   │   ├── models.py                   # SQLAlchemy models (Learner, path models)
│   │   ├── database.py                 # SQLite engine configurations
│   │   ├── routers/                    # profile.py, onboarding.py, path.py, etc.
│   │   └── services/                   # recommendation_service.py, onboarding_service.py
│   └── tests/                          # Automated Pytest suite
└── frontend/                           # React SPA source and config assets
    ├── src/
    │   ├── App.jsx                     # Shell layout, theme switcher, animation timer
    │   ├── index.css                   # Custom stylesheets & mode tokens
    │   ├── api/client.js               # REST client mapping routes
    │   ├── context/LearnerContext.jsx  # Global profile state manager
    │   └── pages/                      # OnboardingPage.jsx, ProfilePage.jsx, etc.
    └── package.json
```

---

## 4. Installation & Setup

### Prerequisites
* Python 3.11 or later
* Node.js v18 or later

### 4.1 Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows (Powershell)
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and configure variables (optional: add `GEMINI_API_KEY` to enable Google Gemini AI. Otherwise, LearnPath runs its deterministic local NLP and pedagogical fallback offline):
   ```bash
   copy .env.example .env
   ```
5. Start the FastAPI backend server:
   ```bash
   python run.py
   ```
   *(Note: The FastAPI application automatically initializes the database file, creates all tables, and seeds the required system reference data on startup. No separate seeding script is needed.)*

### 4.2 Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the web app in your browser at: `http://localhost:5173/`

---

## 5. Testing & Verification

### 5.1 Automated Tests
Run the backend pytest suite to verify adaptive models and database reset hooks:
```bash
cd backend
python -m pytest tests -v
```

### 5.2 Database Reset Dev Route
During development, a database reset can be triggered via a POST request to `/api/profile/reset`. This endpoint cleans up all learner profile records, roadmap paths, assessment scores, and mentor logs, returning the application to a fresh state.

---

## 6. Documentations Directory
Detailed descriptions of the core architectures are located in the [docs](docs/) directory:
* [Primary Solution Report](docs/LearnPath_Solution_Documentation.md): Comprehensive 32-section project documentation package.
* [System Architecture](docs/architecture.md): Visual Mermaid layout and file structural descriptions.
* [Learner Journey Workflow](docs/user_workflow.md): conversational onboarding and adaptive pathway diagrams.
* [Recommendation Logic & DAG](docs/recommendation_logic.md): Topological sort calculations and skill dependencies.
* [Data Models](docs/data_model.md): Detailed database entity relationship schemas.
* [Testing Guide](docs/testing.md): Automated pytest structure and browser test instructions.
