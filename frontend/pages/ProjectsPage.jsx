import React, { useState, useEffect } from 'react';
import { useLearner } from '../context/LearnerContext';
import { api } from '../api/client';
import {
  CodeIcon,
  ClockIcon,
  CheckIcon,
  MessageSquareIcon,
  XIcon
} from '../components/Icons';

export default function ProjectsPage() {
  const { activeLearner, openFeedback, openMentorWithContext, showToast, refreshDashboard } = useLearner();

  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [repoUrl, setRepoUrl] = useState('');
  const [projectNotes, setProjectNotes] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const params = {};
      if (activeLearner) {
        params.domain = activeLearner.direction;
        params.learner_id = activeLearner.id;
      }
      const data = await api.getProjects(params);
      setProjects(data);
    } catch (err) {
      console.error('Failed to load projects:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [activeLearner]);

  const handleUpdateStatus = async (projectId, newStatus) => {
    if (!activeLearner) return;
    try {
      await api.updateProjectProgress(projectId, activeLearner.id, {
        status: newStatus,
        repo_url: repoUrl,
        notes: projectNotes,
      });
      showToast(`Project marked as ${newStatus}`, 'success');
      await fetchProjects();
      await refreshDashboard();
      if (selectedProject && selectedProject.id === projectId) {
        setSelectedProject({ ...selectedProject, user_status: newStatus, repo_url: repoUrl, notes: projectNotes });
      }
    } catch (err) {
      showToast('Error updating project: ' + err.message, 'error');
    }
  };

  const openProjectDetail = (p) => {
    setSelectedProject(p);
    setRepoUrl(p.repo_url || '');
    setProjectNotes(p.notes || '');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-main)' }}>
          EXPLORE PROJECTS
        </h2>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '13.5px', marginTop: '2px' }}>
          Discover practical projects that can become part of your learning journey.
        </p>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-muted)' }}>
          Loading projects...
        </div>
      ) : projects.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: 'var(--color-text-muted)' }}>No projects found for current track.</p>
        </div>
      ) : (
        <div className="grid-2">
          {projects.map((p) => {
            const isCompleted = p.user_status === 'completed';
            const isInProgress = p.user_status === 'in_progress';

            return (
              <div key={p.id} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span className="badge badge-upcoming">{p.topic}</span>
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
                    fontSize: '15.5px',
                    fontWeight: 600,
                    marginBottom: '6px',
                    color: 'var(--color-text-main)',
                    cursor: 'pointer',
                  }}
                  onClick={() => openProjectDetail(p)}
                >
                  {p.title}
                </h3>

                <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.45, flex: 1, marginBottom: '12px' }}>
                  {p.objective}
                </p>

                <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '10px', fontSize: '12px', color: 'var(--color-text-muted)', marginBottom: '12px' }}>
                  <span>{p.required_skills}</span>
                  <span>·</span>
                  <span>Requires: {p.prerequisites || 'None'}</span>
                  <span>·</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <ClockIcon size={12} />
                    <span>~{p.estimated_hours} hrs</span>
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', borderTop: '1px solid var(--color-border-subtle)' }}>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => openProjectDetail(p)}
                  >
                    Instructions & Guide
                  </button>

                  {activeLearner && (
                    <div style={{ display: 'flex', gap: '6px' }}>
                      {!isCompleted ? (
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => openProjectDetail(p)}
                        >
                          {isInProgress ? 'Submit Deliverable' : 'Start Project'}
                        </button>
                      ) : (
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => openProjectDetail(p)}
                        >
                          Review Submission
                        </button>
                      )}
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => openFeedback({ id: p.id, title: p.title, type: 'project' })}
                        title="Submit feedback"
                      >
                        <MessageSquareIcon size={13} />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Project Detail Modal */}
      {selectedProject && (
        <div className="modal-overlay" onClick={() => setSelectedProject(null)}>
          <div className="modal-dialog" style={{ maxWidth: '580px' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
              <div>
                <span className="badge badge-upcoming">{selectedProject.topic}</span>
                <h3 style={{ fontSize: '17px', fontWeight: 700, marginTop: '4px' }}>
                  {selectedProject.title}
                </h3>
                <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                  Difficulty: {selectedProject.difficulty} • ~{selectedProject.estimated_hours} hrs
                </div>
              </div>
              <button
                onClick={() => setSelectedProject(null)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}
              >
                <XIcon size={18} />
              </button>
            </div>

            {/* Objective */}
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '2px' }}>
                Objective
              </div>
              <p style={{ fontSize: '13px', lineHeight: 1.5, color: 'var(--color-text-secondary)' }}>
                {selectedProject.objective}
              </p>
            </div>

            {/* Prerequisites */}
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '2px' }}>
                Prerequisites & Required Skills
              </div>
              <p style={{ fontSize: '12.5px', color: 'var(--color-text-secondary)', margin: 0 }}>
                {selectedProject.prerequisites ? `${selectedProject.prerequisites} • ` : ''}{selectedProject.required_skills}
              </p>
            </div>

            {/* Steps */}
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '4px' }}>
                Suggested Steps
              </div>
              <ul style={{ paddingLeft: '18px', fontSize: '12.5px', lineHeight: 1.5, color: 'var(--color-text-secondary)' }}>
                {selectedProject.suggested_steps ? (
                  JSON.parse(selectedProject.suggested_steps).map((step, idx) => (
                    <li key={idx} style={{ marginBottom: '3px' }}>
                      {step}
                    </li>
                  ))
                ) : (
                  <li style={{ marginBottom: '3px' }}>Design and implement the custom specifications.</li>
                )}
              </ul>
            </div>

            {/* Expected Outcome */}
            <div style={{ background: 'var(--color-surface-subtle)', padding: '10px 12px', borderRadius: 'var(--radius-md)', marginBottom: '14px' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '2px' }}>
                Expected Deliverable
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--color-text-secondary)' }}>
                {selectedProject.expected_outcome}
              </div>
            </div>

            {/* Optional Metadata */}
            {activeLearner && (
              <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '12px', marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>
                  Repository / Project URL (Optional)
                </label>
                <input
                  type="text"
                  className="text-input-clean"
                  style={{ width: '100%', marginBottom: '8px' }}
                  placeholder="https://github.com/username/project"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                />

                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>
                  Implementation Notes (Optional)
                </label>
                <textarea
                  className="text-input-clean"
                  style={{ width: '100%', height: '50px' }}
                  placeholder="Brief summary of challenges solved or architecture used..."
                  value={projectNotes}
                  onChange={(e) => setProjectNotes(e.target.value)}
                />
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => openMentorWithContext(selectedProject.title)}
              >
                Ask Mentor
              </button>

              {activeLearner && (
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => {
                      handleUpdateStatus(selectedProject.id, 'in_progress');
                      setSelectedProject(null);
                    }}
                  >
                    Mark In Progress
                  </button>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => {
                      handleUpdateStatus(selectedProject.id, 'completed');
                      setSelectedProject(null);
                    }}
                  >
                    Mark Completed
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
