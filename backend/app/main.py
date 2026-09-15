from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed_data import seed_database

# Routers
from app.routers.onboarding import router as onboarding_router
from app.routers.profile import router as profile_router
from app.routers.paths import router as paths_router
from app.routers.resources import router as resources_router
from app.routers.projects import router as projects_router
from app.routers.assessments import router as assessments_router
from app.routers.feedback import router as feedback_router
from app.routers.mentor import router as mentor_router
from app.routers.dashboard import router as dashboard_router

# Initialize SQLite tables on module load
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    # Seed knowledge base
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api
app.include_router(onboarding_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(paths_router, prefix="/api")
app.include_router(resources_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(assessments_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(mentor_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "gemini_configured": bool(settings.GEMINI_API_KEY)
    }
