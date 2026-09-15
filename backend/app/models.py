import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base

class Learner(Base):
    __tablename__ = "learners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="Learner")
    target_goal = Column(String(255), nullable=False)
    direction = Column(String(100), default="Cloud / DevOps")
    current_knowledge = Column(Text, default="[]")  # JSON string of skill names
    current_level = Column(String(50), default="Beginner")
    available_time = Column(String(100), default="1-2 hours daily")
    target_timeline = Column(String(100), default="3 months")
    learning_preference = Column(String(100), default="Practical / Project-based")
    weak_areas = Column(Text, default="[]")  # JSON array
    areas_to_explore = Column(Text, default="[]")  # JSON array
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    paths = relationship("LearningPath", back_populates="learner", cascade="all, delete-orphan")
    progress_records = relationship("LearnerProgress", back_populates="learner", cascade="all, delete-orphan")
    project_progress = relationship("LearnerProjectProgress", back_populates="learner", cascade="all, delete-orphan")
    assessment_attempts = relationship("LearnerAssessmentAttempt", back_populates="learner", cascade="all, delete-orphan")
    feedback_records = relationship("LearnerFeedback", back_populates="learner", cascade="all, delete-orphan")
    milestones = relationship("LearnerMilestone", back_populates="learner", cascade="all, delete-orphan")
    mentor_messages = relationship("MentorMessage", back_populates="learner", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    domain = Column(String(100), index=True, nullable=False)  # Cloud/DevOps, Full-Stack, AI/ML, Data Engineering
    category = Column(String(100), default="General")
    description = Column(Text, default="")
    difficulty_level = Column(String(50), default="Beginner")  # Beginner, Intermediate, Advanced

    # Relationships
    resources = relationship("LearningResource", back_populates="skill")
    assessments = relationship("Assessment", back_populates="skill")


class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    prerequisite_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    strength = Column(String(50), default="required")  # required, recommended


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(50), default="Beginner")
    prerequisites_summary = Column(String(255), default="None")
    estimated_hours = Column(Float, default=3.0)
    resource_type = Column(String(50), default="Tutorial")  # Course, Tutorial, Lab, Documentation
    url = Column(String(500), default="")
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    key_takeaways = Column(Text, default="")

    skill = relationship("Skill", back_populates="resources")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    title = Column(String(255), nullable=False)
    domain = Column(String(100), default="")
    target_goal = Column(String(255), default="")
    description = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    learner = relationship("Learner", back_populates="paths")
    items = relationship("LearningPathItem", back_populates="path", cascade="all, delete-orphan", order_by="LearningPathItem.stage_order")


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    stage_order = Column(Integer, nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    why_recommended = Column(Text, default="")
    prerequisites_summary = Column(String(255), default="None")
    estimated_hours = Column(Float, default=4.0)
    status = Column(String(50), default="available")  # completed, in_progress, available, locked, skipped
    is_adaptive_remedial = Column(Boolean, default=False)
    remedial_reason = Column(String(255), default="")
    practice_notes = Column(Text, default="")

    path = relationship("LearningPath", back_populates="items")
    skill = relationship("Skill")


class LearnerProgress(Base):
    __tablename__ = "learner_progress"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("learning_resources.id"), nullable=False)
    status = Column(String(50), default="not_started")  # not_started, in_progress, completed
    time_spent_minutes = Column(Integer, default=0)
    notes = Column(Text, default="")
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    learner = relationship("Learner", back_populates="progress_records")
    resource = relationship("LearningResource")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=False)
    topic = Column(String(100), default="")
    objective = Column(Text, nullable=False)
    difficulty = Column(String(50), default="Intermediate")
    required_skills = Column(String(255), default="")
    prerequisites = Column(String(255), default="")
    estimated_hours = Column(Float, default=6.0)
    suggested_steps = Column(Text, default="[]")  # JSON array of steps
    expected_outcome = Column(Text, default="")
    related_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)

    skill = relationship("Skill")


class LearnerProjectProgress(Base):
    __tablename__ = "learner_project_progress"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(String(50), default="not_started")  # not_started, in_progress, completed
    notes = Column(Text, default="")
    repo_url = Column(String(500), default="")  # Optional learner project link
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    learner = relationship("Learner", back_populates="project_progress")
    project = relationship("Project")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    passing_percentage = Column(Integer, default=70)
    description = Column(Text, default="")

    skill = relationship("Skill", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON array of 4 options
    correct_option_index = Column(Integer, nullable=False)  # 0 to 3
    explanation = Column(Text, default="")

    assessment = relationship("Assessment", back_populates="questions")


class LearnerAssessmentAttempt(Base):
    __tablename__ = "learner_assessment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    passed = Column(Boolean, default=False)
    weak_areas = Column(Text, default="[]")  # JSON array of detected weak topics
    submitted_answers = Column(Text, default="[]")  # JSON array of learner choices
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    learner = relationship("Learner", back_populates="assessment_attempts")
    assessment = relationship("Assessment")


class LearnerFeedback(Base):
    __tablename__ = "learner_feedback"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    item_type = Column(String(50), default="stage")  # stage, resource, assessment, general
    item_id = Column(Integer, nullable=True)
    item_title = Column(String(255), default="")
    rating = Column(String(50), nullable=False)  # easy, good, difficult, very_difficult
    comment = Column(Text, default="")
    action_applied = Column(String(255), default="")  # e.g., "Inserted refresher", "Marked fast-track"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    learner = relationship("Learner", back_populates="feedback_records")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    badge_icon = Column(String(50), default="trophy")
    requirement_type = Column(String(50), nullable=False)  # first_topic, skill_count, first_project, first_assessment, path_complete
    requirement_value = Column(Integer, default=1)


class LearnerMilestone(Base):
    __tablename__ = "learner_milestones"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.datetime.utcnow)

    learner = relationship("Learner", back_populates="milestones")
    milestone = relationship("Milestone")


class MentorMessage(Base):
    __tablename__ = "mentor_messages"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # "user" or "mentor"
    content = Column(Text, nullable=False)
    context_tag = Column(String(100), default="")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    learner = relationship("Learner", back_populates="mentor_messages")
