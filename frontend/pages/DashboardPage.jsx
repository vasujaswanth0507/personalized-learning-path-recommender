import React, { useEffect, useState } from 'react';
import { useLearner } from '../context/LearnerContext';
import {
  RoadmapIcon,
  BookOpenIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  MessageSquareIcon,
  AwardIcon
} from '../components/Icons';

export default function DashboardPage({ setActivePage }) {
  const {
    activeLearner,
    dashboardData,
    refreshDashboard,
    openFeedback,
  } = useLearner();

  const [isExplanationExpanded, setIsExplanationExpanded] = useState(false);

  useEffect(() => {
    if (activeLearner) {
      refreshDashboard();
    }
  }, [activeLearner]);

  if (!activeLearner) {
    return (
      <div className="dashboard-fresh-state">
        <div className="fresh-hero-card">
          <h2 className="fresh-hero-title">WELCOME TO LEARNPATH</h2>
          <p className="fresh-hero-subtitle">Build a learning journey around your goals.</p>
          <button className="btn btn-primary" onClick={() => setActivePage('onboarding')} style={{ marginTop: '12px' }}>
            <span>Start Your Journey</span>
            <ArrowRightIcon size={14} />
          </button>
        </div>

        <div className="fresh-explanation-section">
          <h3 className="fresh-section-title">How It Works</h3>
          <div className="fresh-steps-grid">
            <div className="fresh-step-card">
              <span className="step-num-badge">1</span>
              <div style={{ flex: 1 }}>
                <h4 className="step-card-title">Tell us where you want to go</h4>
                <p className="step-card-desc">State your desired career role or learning target in free-form language.</p>
              </div>
            </div>
            <div className="fresh-step-card">
              <span className="step-num-badge">2</span>
              <div style={{ flex: 1 }}>
                <h4 className="step-card-title">Understand where you are</h4>
                <p className="step-card-desc">Credit your prior experiences and certifications to fast-track foundational material.</p>
              </div>
            </div>
            <div className="fresh-step-card">
              <span className="step-num-badge">3</span>
              <div style={{ flex: 1 }}>
                <h4 className="step-card-title">Identify what you need</h4>
                <p className="step-card-desc">Your Mentor determines the required skills and plans the ideal sequence for you.</p>
              </div>
            </div>
            <div className="fresh-step-card">
              <span className="step-num-badge">4</span>
              <div style={{ flex: 1 }}>
                <h4 className="step-card-title">Build your learning path</h4>
                <p className="step-card-desc">Get a personalized, chronological roadmap containing structured stages and resources.</p>
              </div>
            </div>
            <div className="fresh-step-card">
              <span className="step-num-badge">5</span>
              <div style={{ flex: 1 }}>
                <h4 className="step-card-title">Learn, practice and adapt</h4>
                <p className="step-card-desc">Submit feedback on stage difficulty or fail assessments to trigger remedial inserts dynamically.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const d = dashboardData || {
    learner_name: activeLearner.name,
    target_goal: activeLearner.target_goal,
    direction: activeLearner.direction,
    overall_progress_pct: 0,
    completed_items_count: 0,
    total_items_count: 0,
    current_learning_item: activeLearner.direction || 'Calculating active stage...',
    next_recommended_action: 'Determining recommendations...',
    skill_mastery: [],
    milestones: [],
    recent_feedback: [],
  };

  const getGreeting = () => {
    const hr = new Date().getHours();
    let greet = 'Welcome back';
    if (hr < 12) greet = 'Good morning';
    else if (hr < 17) greet = 'Good afternoon';
    else greet = 'Good evening';

    if (d.learner_name && d.learner_name.trim()) {
      return `${greet}, ${d.learner_name}`;
    }
    return greet;
  };

  return (
    <div className="dashboard-container">
      {/* Top Welcome Title Area */}
      <header className="dashboard-header-greet">
        <div>
          <h2 className="dashboard-greeting-title">
            {getGreeting()}
          </h2>
          <div className="dashboard-sub-target">
            <span>Working toward:</span>
            <strong>{d.target_goal || d.direction}</strong>
          </div>
        </div>
        <div className="dashboard-header-actions desktop-only">
          <button className="btn btn-secondary btn-sm" onClick={() => setActivePage('path')}>
            <RoadmapIcon size={14} />
            <span>Roadmap</span>
          </button>
        </div>
      </header>

      {/* Hero Continue Learning Area - Spans Full Width */}
      <section className="dashboard-continue-section">
        <div className="dashboard-continue-banner">
          <div className="continue-banner-content">
            <span className="continue-current-tag">Current Stage</span>
            <h4 className="continue-item-title">{d.current_learning_item}</h4>
            <p className="continue-item-time">
              Estimate: 4.5 hours to master this stage
            </p>
            <div style={{ marginTop: '16px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={() => setActivePage('resources')}>
                <span>Continue Learning</span>
                <ArrowRightIcon size={14} />
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => openFeedback({ id: null, title: d.current_learning_item, type: 'stage' })}
                title="Provide feedback on this stage"
              >
                <MessageSquareIcon size={14} />
                <span>Feedback</span>
              </button>
            </div>
          </div>
          <div className="continue-banner-progress">
            <div className="radial-progress-dummy" style={{ '--percent': d.overall_progress_pct }}>
              <div className="radial-inner">
                <span className="radial-value">{d.overall_progress_pct}%</span>
                <span className="radial-label">Overall Path</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Grid Content */}
      <div className="dashboard-layout">
        {/* Left Column: Focused Continuation and Actions */}
        <div className="dashboard-main-col">
          {/* Next Recommended Action Area */}
          <section className="dashboard-action-section">
            <h3 className="dashboard-section-label">Next Step</h3>
            <div className="dashboard-action-card">
              <div className="action-card-header">
                <AwardIcon size={16} className="text-primary" />
                <h4 className="action-card-title">{d.next_recommended_action}</h4>
              </div>
              <p className="action-card-reason">
                This builds directly on your current stage to unlock downstream learning track dependencies.
              </p>
              
              {isExplanationExpanded && (
                <p className="action-card-why-details">
                  By completing this next recommended step, you satisfy prerequisite requirements in the domain DAG. This ensures you master core fundamentals before taking on advanced projects and assessments.
                </p>
              )}

              <div style={{ display: 'flex', gap: '10px', marginTop: '14px', flexWrap: 'wrap' }}>
                <button className="btn btn-primary btn-sm" onClick={() => setActivePage('path')}>
                  Continue Roadmap
                </button>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => setIsExplanationExpanded(!isExplanationExpanded)}
                >
                  {isExplanationExpanded ? 'Hide Details' : 'Why this step?'}
                </button>
              </div>
            </div>
          </section>

          {/* Recent Activity and feedback */}
          <section className="dashboard-activity-section">
            <h3 className="dashboard-section-label">Recent Activity & Feedback</h3>
            {d.recent_feedback.length > 0 ? (
              <div className="dashboard-activity-list">
                {d.recent_feedback.map((fb) => (
                  <div key={fb.id} className="dashboard-activity-item">
                    <div className="activity-item-header">
                      <span className="activity-item-title">{fb.item_title}</span>
                      <span className="badge badge-completed">{fb.rating}</span>
                    </div>
                    {fb.action_applied && (
                      <p className="activity-item-meta">
                        Adaptation Applied: {fb.action_applied}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="dashboard-empty-note">
                No learning feedback logged yet. Providing feedback on stages tailors your roadmap items dynamically.
              </p>
            )}
          </section>
        </div>

        {/* Right Column: Progress and Supporting Metadata */}
        <aside className="dashboard-side-col">
          {/* Your Progress */}
          <section className="dashboard-progress-section">
            <h3 className="dashboard-section-label">Your Progress</h3>
            <div className="progress-summary-block">
              <div className="progress-top-row">
                <div className="progress-main-stat">
                  <span className="progress-score-large">{d.overall_progress_pct}%</span>
                  <span className="progress-sub-label">Overall journey</span>
                </div>
                <div className="progress-sub-stat">
                  <span className="progress-score-medium">
                    {d.completed_items_count} <span style={{ fontSize: '13.5px', fontWeight: 500, color: 'var(--color-text-muted)' }}>/ {d.total_items_count}</span>
                  </span>
                  <span className="progress-sub-label">stages complete</span>
                </div>
              </div>
              <div className="progress-bar-container" style={{ margin: '14px 0 6px 0' }}>
                <div
                  className="progress-bar-fill"
                  style={{ width: `${d.overall_progress_pct}%` }}
                />
              </div>
            </div>

            {/* Skill Development */}
            <div className="dashboard-skills-list">
              <h4 className="dashboard-sub-section-title">Skill Competencies</h4>
              {d.skill_mastery.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  {d.skill_mastery.map((s, idx) => {
                    const isStrong = s.percentage >= 80;
                    const isNotStarted = s.percentage === 0;
                    let badgeLabel = 'Developing';
                    let badgeClass = 'badge-developing';
                    if (isStrong) {
                      badgeLabel = 'Strong';
                      badgeClass = 'badge-strong';
                    } else if (isNotStarted) {
                      badgeLabel = 'Not Started';
                      badgeClass = 'badge-not-started';
                    }

                    return (
                      <div key={idx} className="dashboard-skill-row">
                        <div className="skill-row-info">
                          <div style={{ display: 'flex', alignItems: 'center' }}>
                            <span className="skill-name">{s.skill_name}</span>
                            <span className={`skill-status-badge ${badgeClass}`}>{badgeLabel}</span>
                          </div>
                          <span className="skill-val">{s.percentage}%</span>
                        </div>
                        <div className="progress-bar-container mini">
                          <div
                            className="progress-bar-fill"
                            style={{
                              width: `${s.percentage}%`,
                              backgroundColor: isStrong
                                ? 'var(--success-text)'
                                : isNotStarted
                                  ? 'var(--color-border)'
                                  : 'var(--primary-600)'
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="dashboard-empty-note">No competencies tracked yet. Start learning to record skills.</p>
              )}
            </div>
          </section>

          {/* Your Journey Timeline */}
          <section className="dashboard-journey-section">
            <h3 className="dashboard-section-label">Your Journey</h3>
            <div className="dashboard-timeline-vertical">
              {d.milestones.slice(0, 4).map((m, idx) => {
                const isNext = !m.is_unlocked && (idx === 0 || d.milestones[idx - 1]?.is_unlocked);
                return (
                  <div
                    key={m.id}
                    className={`timeline-node-item ${m.is_unlocked ? 'is-complete' : isNext ? 'is-next' : 'is-upcoming'}`}
                  >
                    <div className="timeline-node-dot">
                      {m.is_unlocked && <CheckCircleIcon size={12} />}
                    </div>
                    <div className="timeline-node-content">
                      <h4 className="timeline-node-title">{m.title}</h4>
                      <p className="timeline-node-desc">
                        {m.is_unlocked
                          ? `Achieved ${m.unlocked_at || ''}`
                          : isNext
                            ? 'Current Milestone Goal'
                            : 'Locked Milestone'}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}
