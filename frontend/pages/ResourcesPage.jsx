import React, { useState, useEffect } from 'react';
import { useLearner } from '../context/LearnerContext';
import { api } from '../api/client';
import {
  SearchIcon,
  BookOpenIcon,
  ClockIcon,
  CheckIcon,
  ExternalLinkIcon,
  MessageSquareIcon,
  XIcon
} from '../components/Icons';

export default function ResourcesPage() {
  const { activeLearner, openFeedback, openMentorWithContext, showToast, refreshDashboard } = useLearner();

  const [resources, setResources] = useState([]);
  const [filterDomain, setFilterDomain] = useState(activeLearner?.direction || '');
  const [searchTopic, setSearchTopic] = useState('');
  const [selectedResource, setSelectedResource] = useState(null);
  const [studyMinutes, setStudyMinutes] = useState(30);
  const [studyNotes, setStudyNotes] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchResources = async () => {
    setIsLoading(true);
    try {
      const params = {};
      if (filterDomain) params.domain = filterDomain;
      if (searchTopic) params.topic = searchTopic;
      if (activeLearner) params.learner_id = activeLearner.id;

      const data = await api.getResources(params);
      setResources(data);
    } catch (err) {
      console.error('Failed to load resources:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchResources();
  }, [filterDomain, searchTopic, activeLearner]);

  const handleUpdateStatus = async (resourceId, newStatus) => {
    if (!activeLearner) return;
    try {
      await api.updateResourceProgress(resourceId, activeLearner.id, {
        status: newStatus,
        time_spent_minutes: studyMinutes,
        notes: studyNotes,
      });
      showToast(`Resource marked as ${newStatus}`, 'success');
      await fetchResources();
      await refreshDashboard();
      if (selectedResource && selectedResource.id === resourceId) {
        setSelectedResource({ ...selectedResource, user_status: newStatus });
      }
    } catch (err) {
      showToast('Progress update error: ' + err.message, 'error');
    }
  };

  // Determine sections based on personalization availability
  const hasPersonalization = activeLearner && !filterDomain && !searchTopic;
  
  const recommendedList = hasPersonalization
    ? resources.filter((r) => r.domain === activeLearner.direction)
    : [];

  const exploreList = hasPersonalization
    ? resources.filter((r) => r.domain !== activeLearner.direction)
    : resources;

  const renderResourceCard = (r) => {
    const isCompleted = r.user_status === 'completed';
    const isInProgress = r.user_status === 'in_progress';

    return (
      <div key={r.id} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <span className="badge badge-upcoming">{r.resource_type}</span>
          {activeLearner && (
            <span
              className={`badge ${
                isCompleted
                  ? 'badge-completed'
                  : isInProgress
                  ? 'badge-current'
                  : 'badge-locked'
              }`}
            >
              {isCompleted && <CheckIcon size={11} />}
              {isCompleted
                ? 'Completed'
                : isInProgress
                ? 'In Progress'
                : 'Not Started'}
            </span>
          )}
        </div>

        <h3
          style={{
            fontSize: '15px',
            fontWeight: 600,
            marginBottom: '4px',
            color: 'var(--color-text-main)',
            cursor: 'pointer',
          }}
          onClick={() => setSelectedResource(r)}
        >
          {r.title}
        </h3>

        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.45, flex: 1, marginBottom: '12px' }}>
          {r.description}
        </p>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: 'var(--color-text-muted)', marginBottom: '12px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <ClockIcon size={13} />
            <span>{r.estimated_hours} hrs</span>
          </span>
          <span>·</span>
          <span>{r.difficulty}</span>
          <span>·</span>
          <span>{r.prerequisites_summary}</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', borderTop: '1px solid var(--color-border-subtle)' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setSelectedResource(r)}
          >
            View Details
          </button>

          {activeLearner && (
            <div style={{ display: 'flex', gap: '6px' }}>
              {!isCompleted ? (
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => handleUpdateStatus(r.id, 'completed')}
                >
                  Mark Complete
                </button>
              ) : (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => handleUpdateStatus(r.id, 'not_started')}
                >
                  Undo
                </button>
              )}
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => openFeedback({ id: r.id, title: r.title, type: 'resource' })}
                title="Submit feedback"
              >
                <MessageSquareIcon size={13} />
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-main)' }}>
          Explore Resources
        </h2>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '13.5px', marginTop: '2px' }}>
          Browse the learning resources available in LearnPath.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ padding: '12px 16px', display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: 1, minWidth: '220px', position: 'relative', display: 'flex', alignItems: 'center' }}>
          <SearchIcon size={15} className="text-muted" style={{ position: 'absolute', left: '10px' }} />
          <input
            type="text"
            className="text-input-clean"
            style={{ width: '100%', paddingLeft: '32px' }}
            placeholder="Search topic (e.g. Linux, Docker, React, SQL)..."
            value={searchTopic}
            onChange={(e) => setSearchTopic(e.target.value)}
          />
        </div>

        <div>
          <select
            className="text-input-clean"
            value={filterDomain}
            onChange={(e) => setFilterDomain(e.target.value)}
          >
            <option value="">All Tracks</option>
            <option value="Cloud / DevOps">Cloud / DevOps</option>
            <option value="Full-Stack Web">Full-Stack Web</option>
            <option value="AI & Machine Learning">AI & Machine Learning</option>
            <option value="Data Engineering">Data Engineering</option>
            <option value="UI/UX Design">UI/UX Design</option>
          </select>
        </div>
      </div>

      {/* Resource Sections Grid */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-muted)' }}>
          Loading resources...
        </div>
      ) : resources.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: 'var(--color-text-muted)' }}>No resources found matching criteria.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
          
          {/* Section 1: Recommended for You */}
          {hasPersonalization && recommendedList.length > 0 && (
            <div>
              <h3 className="dashboard-section-label" style={{ marginBottom: '14px' }}>
                Recommended for You
              </h3>
              <div className="grid-2">
                {recommendedList.map(renderResourceCard)}
              </div>
              <hr className="dashboard-divider" style={{ marginTop: '24px' }} />
            </div>
          )}

          {/* Section 2: Explore Library catalog */}
          <div>
            {hasPersonalization && (
              <h3 className="dashboard-section-label" style={{ marginBottom: '14px' }}>
                Explore Library
              </h3>
            )}
            <div className="grid-2">
              {exploreList.map(renderResourceCard)}
            </div>
          </div>

        </div>
      )}

      {/* Detailed Modal view */}
      {selectedResource && (
        <div className="modal-overlay" onClick={() => setSelectedResource(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
              <div>
                <span className="badge badge-upcoming" style={{ marginBottom: '6px' }}>{selectedResource.resource_type}</span>
                <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-text-main)' }}>{selectedResource.title}</h2>
              </div>
              <button className="btn-icon-only" onClick={() => setSelectedResource(null)}>
                <XIcon size={18} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '13.5px' }}>
              <div>
                <span style={{ color: 'var(--color-text-muted)' }}>Description: </span>
                <p style={{ color: 'var(--color-text-secondary)', marginTop: '4px', lineHeight: '1.5' }}>{selectedResource.description}</p>
              </div>

              {selectedResource.key_takeaways && (
                <div>
                  <span style={{ color: 'var(--color-text-muted)', fontWeight: 600 }}>Key Takeaways:</span>
                  <p style={{ color: 'var(--color-text-secondary)', marginTop: '4px', fontStyle: 'italic' }}>{selectedResource.key_takeaways}</p>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', padding: '10px 14px', background: 'var(--color-surface-subtle)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Difficulty:</span>
                  <div style={{ fontWeight: 600 }}>{selectedResource.difficulty}</div>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Prerequisites:</span>
                  <div style={{ fontWeight: 600 }}>{selectedResource.prerequisites_summary}</div>
                </div>
              </div>

              {activeLearner && (
                <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '14px', marginTop: '6px' }}>
                  <h4 style={{ fontWeight: 600, marginBottom: '10px' }}>Log Your Progress</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <label style={{ fontSize: '12.5px', color: 'var(--color-text-muted)' }}>Time Spent (minutes):</label>
                      <input
                        type="number"
                        className="text-input-clean"
                        style={{ width: '80px', padding: '4px 8px' }}
                        value={studyMinutes}
                        onChange={(e) => setStudyMinutes(parseInt(e.target.value, 10) || 0)}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '12.5px', color: 'var(--color-text-muted)', display: 'block', marginBottom: '4px' }}>Study Notes:</label>
                      <textarea
                        className="text-input-clean"
                        style={{ width: '100%', minHeight: '60px', padding: '8px' }}
                        placeholder="What did you learn? Track your insights..."
                        value={studyNotes}
                        onChange={(e) => setStudyNotes(e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: '10px', marginTop: '10px', justifyContent: 'flex-end' }}>
                {selectedResource.url && (
                  <a
                    href={selectedResource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary btn-sm"
                    style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                  >
                    <span>Go to Resource</span>
                    <ExternalLinkIcon size={12} />
                  </a>
                )}
                {activeLearner && (
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => {
                      handleUpdateStatus(selectedResource.id, 'completed');
                      setSelectedResource(null);
                    }}
                  >
                    Mark as Completed
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
