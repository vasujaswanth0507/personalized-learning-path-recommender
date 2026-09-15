from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

# --- Onboarding Schemas ---
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class OnboardingRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    current_extracted: Dict[str, Any] = {}

class OnboardingResponse(BaseModel):
    reply: str
    extracted_profile: Dict[str, Any]
    is_ready_for_profile: bool
    suggested_chips: List[str] = []

# --- Learner Profile Schemas ---
class LearnerProfileBase(BaseModel):
    name: str = "Learner"
    target_goal: str
    direction: str = "Cloud / DevOps"
    current_knowledge: List[str] = []
    current_level: str = "Beginner"
    available_time: str = "1-2 hours daily"
    target_timeline: str = "3 months"
    learning_preference: str = "Practical / Project-based"
    weak_areas: List[str] = []
    areas_to_explore: List[str] = []
    notes: str = ""

class LearnerProfileCreate(LearnerProfileBase):
    pass

class LearnerProfileUpdate(BaseModel):
    name: Optional[str] = None
    target_goal: Optional[str] = None
    direction: Optional[str] = None
    current_knowledge: Optional[List[str]] = None
    current_level: Optional[str] = None
    available_time: Optional[str] = None
    target_timeline: Optional[str] = None
    learning_preference: Optional[str] = None
    weak_areas: Optional[List[str]] = None
    areas_to_explore: Optional[List[str]] = None
    notes: Optional[str] = None

class LearnerProfileResponse(LearnerProfileBase):
    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

# --- Learning Path Schemas ---
class LearningPathItemResponse(BaseModel):
    id: int
    stage_order: int
    skill_id: Optional[int]
    title: str
    description: str
    why_recommended: str
    prerequisites_summary: str
    estimated_hours: float
    status: str  # completed, in_progress, available, locked, skipped
    is_adaptive_remedial: bool
    remedial_reason: str
    practice_notes: str

class LearningPathResponse(BaseModel):
    id: int
    learner_id: int
    title: str
    domain: str
    target_goal: str
    description: str
    is_active: bool
    items: List[LearningPathItemResponse]

# --- Resources Schemas ---
class LearningResourceResponse(BaseModel):
    id: int
    title: str
    topic: str
    domain: str
    description: str
    difficulty: str
    prerequisites_summary: str
    estimated_hours: float
    resource_type: str
    url: str
    user_status: str = "not_started"
    key_takeaways: str = ""
    skill_id: Optional[int] = None

class ResourceProgressUpdate(BaseModel):
    status: str  # not_started, in_progress, completed
    time_spent_minutes: int = 0
    notes: str = ""

# --- Projects Schemas ---
class ProjectResponse(BaseModel):
    id: int
    title: str
    domain: str
    topic: str
    objective: str
    difficulty: str
    required_skills: str
    prerequisites: str
    estimated_hours: float
    suggested_steps: List[str]
    expected_outcome: str
    user_status: str = "not_started"
    repo_url: str = ""
    notes: str = ""

class ProjectProgressUpdate(BaseModel):
    status: str  # not_started, in_progress, completed
    repo_url: str = ""
    notes: str = ""

# --- Assessments Schemas ---
class AssessmentQuestionResponse(BaseModel):
    id: int
    question_text: str
    options: List[str]

class AssessmentResponse(BaseModel):
    id: int
    title: str
    topic: str
    domain: str
    passing_percentage: int
    description: str
    questions: List[AssessmentQuestionResponse]

class AssessmentSubmissionRequest(BaseModel):
    answers: List[int]  # List of selected option indices (0 to 3)

class QuestionResultItem(BaseModel):
    question_id: int
    question_text: str
    selected_index: int
    correct_index: int
    is_correct: bool
    explanation: str

class AssessmentSubmissionResult(BaseModel):
    attempt_id: int
    score: int
    total_questions: int
    percentage: float
    passed: bool
    weak_areas: List[str]
    question_results: List[QuestionResultItem]
    adaptive_action: Optional[str] = None

# --- Feedback Schemas ---
class FeedbackSubmitRequest(BaseModel):
    item_type: str = "stage"  # stage, resource, assessment, general
    item_id: Optional[int] = None
    item_title: str = ""
    rating: str  # easy, good, difficult, very_difficult
    comment: str = ""

class FeedbackResponse(BaseModel):
    id: int
    rating: str
    comment: str
    action_applied: str
    created_at: str

# --- AI Mentor Schemas ---
class MentorChatRequest(BaseModel):
    message: str
    current_stage: str = ""
    context_topic: str = ""

class MentorChatResponse(BaseModel):
    reply: str
    suggested_followups: List[str] = []

# --- Dashboard & Progress Schemas ---
class SkillMasteryItem(BaseModel):
    skill_name: str
    percentage: int
    status: str  # Mastered, In Progress, Locked

class MilestoneItem(BaseModel):
    id: int
    title: str
    description: str
    badge_icon: str
    is_unlocked: bool
    unlocked_at: Optional[str] = None

class DashboardStatsResponse(BaseModel):
    learner_name: str
    target_goal: str
    direction: str
    overall_progress_pct: int
    completed_items_count: int
    total_items_count: int
    current_learning_item: Optional[str] = None
    next_recommended_action: Optional[str] = None
    skill_mastery: List[SkillMasteryItem]
    milestones: List[MilestoneItem]
    recent_feedback: List[Dict[str, Any]]
