import React, { useState, useEffect } from 'react';
import { useLearner } from '../context/LearnerContext';
import { api } from '../api/client';
import {
  CheckIcon,
  LockIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  RefreshIcon,
  MessageSquareIcon,
  BotIcon,
  BookOpenIcon,
  CheckCircleIcon,
  ArrowRightIcon
} from '../components/Icons';

export default function LearningPathPage({ setActivePage }) {
  const {
    activeLearner,
    openMentorWithContext,
    openFeedback,
    refreshDashboard,
    showToast,
  } = useLearner();

  const [pathData, setPathData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [expandedStages, setExpandedStages] = useState({});

  const fetchPath = async () => {
    if (!activeLearner) return;
    setIsLoading(true);
    try {
      const data = await api.getPath(activeLearner.id);
      setPathData(data);
    } catch (err) {
      console.error('Failed to load path:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPath();
  }, [activeLearner]);

  const toggleExpand = (stageId) => {
    setExpandedStages((prev) => ({
      ...prev,
      [stageId]: !prev[stageId],
    }));
  };

  const handleUpdateStatus = async (itemId, newStatus) => {
    try {
      await api.updatePathItemStatus(itemId, newStatus);
      showToast(`Status updated to ${newStatus}`, 'success');
      await fetchPath();
      await refreshDashboard();
    } catch (err) {
      showToast('Error updating stage: ' + err.message, 'error');
    }
  };

  const handleRegenerate = async () => {
    if (!activeLearner) return;
    setIsRegenerating(true);
    try {
      const data = await api.regeneratePath(activeLearner.id);
      setPathData(data);
      await refreshDashboard();
      showToast('Roadmap recalculated based on profile calibration', 'success');
    } catch (err) {
      showToast('Recalculation error: ' + err.message, 'error');
    } finally {
      setIsRegenerating(false);
    }
  };

  if (!activeLearner) {
    return (
      <div className="fresh-empty-state-panel">
        <h2 className="fresh-empty-title">YOUR ROADMAP</h2>
        <p className="fresh-empty-desc">
          Your personalized roadmap will appear here once we understand what you're working toward.
        </p>
        <button className="btn btn-primary" onClick={() => setActivePage('onboarding')}>
          <span>Start Your Journey</span>
          <ArrowRightIcon size={14} />
        </button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px', color: 'var(--color-text-muted)' }}>
        Loading roadmap...
      </div>
    );
  }

  const totalStages = pathData?.items?.length || 0;
  const getLevelName = (index) => {
    if (totalStages <= 3) {
      if (index === 0) return 'Foundations';
      if (index === 1) return 'Core Competency';
      return 'Advanced Practice';
    }
    const third = Math.ceil(totalStages / 3);
    if (index < third) return 'Level 1: Foundations';
    if (index < 2 * third) return 'Level 2: Core Development';
    return 'Level 3: Advanced Application';
  };

  let lastLevel = '';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-main)' }}>
            {pathData?.title || 'Learning Roadmap'}
          </h2>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '13.5px', marginTop: '2px' }}>
            Goal: {pathData?.target_goal} • Structured sequential dependencies
          </p>
        </div>

        <button
          className="btn btn-secondary btn-sm"
          onClick={handleRegenerate}
          disabled={isRegenerating}
          title="Recalculate dependencies"
        >
          <RefreshIcon size={14} />
          <span>{isRegenerating ? 'Recalculating...' : 'Recalculate Roadmap'}</span>
        </button>
      </div>

      {/* Structured Roadmap Stages */}
      <div className="roadmap-timeline-container">
        {pathData?.items?.map((stage, idx) => {
          const isCompleted = stage.status === 'completed';
          const isCurrent = stage.status === 'in_progress';
          const isLocked = stage.status === 'locked';
          const isRemedial = stage.is_adaptive_remedial;
          const isExpanded = !!expandedStages[stage.id];

          const formattedIndex = String(idx + 1).padStart(2, '0');
          const currentLevel = getLevelName(idx);
          const showLevelHeader = currentLevel !== lastLevel;
          if (showLevelHeader) {
            lastLevel = currentLevel;
          }

          return (
            <React.Fragment key={stage.id}>
              {showLevelHeader && (
                <div className="roadmap-level-header">
                  <h3 className="level-header-title">{currentLevel}</h3>
                  <span className="level-header-line"></span>
                </div>
              )}

              <div
                className={`roadmap-card ${
                  isCompleted
                    ? 'is-completed'
                    : isCurrent
                    ? 'is-current'
                    : isLocked
                    ? 'is-locked'
                    : ''
                } ${isRemedial ? 'is-remedial' : ''}`}
              >
                <div className="roadmap-main-row">
                  {/* Stage Info */}
                  <div className="roadmap-left-info">
                    <div className="stage-number">{formattedIndex}</div>

                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        <h3 className="stage-title">{stage.title}</h3>
                        <span
                          className={`badge ${
                            isCompleted
                              ? 'badge-completed'
                              : isCurrent
                              ? 'badge-current'
                              : isLocked
                              ? 'badge-locked'
                              : 'badge-upcoming'
                          }`}
                        >
                          {isCompleted && <CheckIcon size={12} />}
                          {isLocked && <LockIcon size={11} />}
                          {isRemedial
                            ? 'Refresher'
                            : stage.status.replace('_', ' ').charAt(0).toUpperCase() +
                              stage.status.replace('_', ' ').slice(1)}
                        </span>
                      </div>

                      <div className="stage-meta">
                        {stage.estimated_hours} hrs
                        {stage.prerequisites_summary && stage.prerequisites_summary !== 'None'
                          ? ` · Requires ${stage.prerequisites_summary}`
                          : ' · Foundational'}
                      </div>

                      <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                        {stage.description}
                      </p>
                    </div>
                  </div>

                  {/* Single Primary Action + Toggle */}
                  <div className="roadmap-right-actions">
                    {isCurrent && (
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => setActivePage('resources')}
                      >
                        Continue Learning
                      </button>
                    )}

                    {!isCurrent && !isCompleted && !isLocked && (
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleUpdateStatus(stage.id, 'in_progress')}
                      >
                        Start Learning
                      </button>
                    )}

                    {isCompleted && (
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleUpdateStatus(stage.id, 'in_progress')}
                      >
                        Review
                      </button>
                    )}

                    {isLocked && (
                      <span style={{ fontSize: '12px', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <LockIcon size={13} />
                        <span>Locked</span>
                      </span>
                    )}

                    <button
                      className="btn-icon-only"
                      onClick={() => toggleExpand(stage.id)}
                      title={isExpanded ? 'Collapse details' : 'Expand why recommended & options'}
                      aria-label="Expand details"
                    >
                      {isExpanded ? <ChevronDownIcon size={16} /> : <ChevronRightIcon size={16} />}
                    </button>
                  </div>
                </div>

                {/* Progressive Disclosure Section */}
                {isExpanded && (
                  <div className="accordion-details">
                    {/* Why this recommendation */}
                    <div className="reasoning-callout">
                      <div style={{ fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '2px' }}>
                        Why this recommendation?
                      </div>
                      <div>{stage.why_recommended}</div>
                    </div>

                    {/* Secondary Options */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginTop: '10px' }}>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => setActivePage('resources')}
                        >
                          <BookOpenIcon size={14} />
                          <span>Curated Resources</span>
                        </button>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => setActivePage('assessments')}
                        >
                          <CheckCircleIcon size={14} />
                          <span>Take Assessment</span>
                        </button>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() =>
                            openFeedback({
                              id: stage.id,
                              title: stage.title,
                              type: 'stage',
                            })
                          }
                        >
                          <MessageSquareIcon size={14} />
                          <span>Feedback</span>
                        </button>
                      </div>

                      <div style={{ display: 'flex', gap: '8px' }}>
                        {!isCompleted ? (
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleUpdateStatus(stage.id, 'completed')}
                          >
                            Mark as Completed
                          </button>
                        ) : (
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleUpdateStatus(stage.id, 'available')}
                          >
                            Reopen Stage
                          </button>
                        )}
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => openMentorWithContext(stage.title)}
                        >
                          <BotIcon size={14} />
                          <span>Ask Mentor</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
