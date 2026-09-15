import React, { useState, useEffect } from 'react';
import { useLearner } from '../context/LearnerContext';
import { api } from '../api/client';
import { CheckIcon, RefreshIcon, UserIcon } from '../components/Icons';

export default function ProfilePage({ setActivePage, theme, setTheme }) {
  const {
    activeLearner,
    setActiveLearner,
    refreshLearners,
    refreshDashboard,
    dashboardData,
    showToast,
  } = useLearner();

  const [formData, setFormData] = useState({
    name: '',
    target_goal: '',
    direction: '',
    current_knowledge: [],
    current_level: '',
    available_time: '',
    target_timeline: '',
    learning_preference: '',
    notes: '',
  });

  const [newSkill, setNewSkill] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirmDelete = async () => {
    setIsDeleting(true);
    try {
      await api.deleteProfile(activeLearner.id);
      showToast('Profile and all associated data permanently deleted.', 'success');
      localStorage.removeItem('learnpath_onboarding_learner_id');
      localStorage.removeItem('learnpath_active_learner_id');
      setActiveLearner(null);
      setShowDeleteModal(false);
      await refreshLearners();
      setActivePage('onboarding');
    } catch (err) {
      showToast('Failed to delete profile: ' + err.message, 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  useEffect(() => {
    if (activeLearner) {
      setFormData({
        name: activeLearner.name || 'Learner',
        target_goal: activeLearner.target_goal || '',
        direction: activeLearner.direction || 'Cloud / DevOps',
        current_knowledge: activeLearner.current_knowledge || [],
        current_level: activeLearner.current_level || 'Beginner',
        available_time: activeLearner.available_time || '1-2 hours daily',
        target_timeline: activeLearner.target_timeline || '3 months',
        learning_preference: activeLearner.learning_preference || 'Practical / Project-based',
        notes: activeLearner.notes || '',
      });
    }
  }, [activeLearner]);

  const handleAddSkill = () => {
    if (!newSkill.trim()) return;
    if (!formData.current_knowledge.includes(newSkill.trim())) {
      setFormData({
        ...formData,
        current_knowledge: [...formData.current_knowledge, newSkill.trim()],
      });
    }
    setNewSkill('');
  };

  const handleRemoveSkill = (skill) => {
    setFormData({
      ...formData,
      current_knowledge: formData.current_knowledge.filter((s) => s !== skill),
    });
  };

  const handleSave = async (recalculate = false) => {
    if (!activeLearner) return;
    setIsSaving(true);
    try {
      const updated = await api.updateProfile(activeLearner.id, formData, recalculate);
      setActiveLearner(updated);
      await refreshLearners();
      await refreshDashboard();
      showToast(
        recalculate
          ? 'Profile saved and roadmap dependencies recalculated'
          : 'Profile changes saved successfully',
        'success'
      );
      setIsEditing(false);
    } catch (err) {
      showToast('Save failed: ' + err.message, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  if (!activeLearner) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600 }}>No Learner Profile Selected</h2>
        <button className="btn btn-primary" style={{ marginTop: '14px' }} onClick={() => setActivePage('onboarding')}>
          Start Onboarding
        </button>
      </div>
    );
  }

  const getInitials = (name) => {
    if (!name) return 'LP';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Profile Header View */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
        <div
          style={{
            width: '60px',
            height: '60px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--primary-100)',
            color: 'var(--primary-700)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            fontWeight: 700,
          }}
        >
          {getInitials(activeLearner.name)}
        </div>

        <div style={{ flex: 1, minWidth: '200px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-main)' }}>
              {activeLearner.name}
            </h2>
            <span className="badge badge-current">{activeLearner.direction}</span>
          </div>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '13.5px', marginTop: '2px' }}>
            {activeLearner.target_goal || 'Exploring'} • Level: {activeLearner.current_level}
          </p>
        </div>

        {!isEditing && (
          <button className="btn btn-primary btn-sm" onClick={() => setIsEditing(true)}>
            Edit Profile
          </button>
        )}
      </div>

      {!isEditing ? (
        /* Summary Mode Panel Layout */
        <div className="grid-2">
          {/* Summary Details */}
          <div className="card">
            <div className="card-header-clean">
              <h3 className="card-title-clean">Learning Calibration</h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', fontSize: '14px', marginTop: '4px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '130px 1fr', gap: '8px' }}>
                <span style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Target Goal:</span>
                <strong style={{ color: 'var(--color-text-main)' }}>{activeLearner.target_goal || 'Exploring'}</strong>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '130px 1fr', gap: '8px' }}>
                <span style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Track Direction:</span>
                <span style={{ color: 'var(--color-text-main)' }}>{activeLearner.direction}</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '130px 1fr', gap: '8px' }}>
                <span style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Current Level:</span>
                <span style={{ color: 'var(--color-text-main)' }}>{activeLearner.current_level}</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '130px 1fr', gap: '8px' }}>
                <span style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Daily Study Time:</span>
                <span style={{ color: 'var(--color-text-main)' }}>{activeLearner.available_time}</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '130px 1fr', gap: '8px' }}>
                <span style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Target Timeline:</span>
                <span style={{ color: 'var(--color-text-main)' }}>{activeLearner.target_timeline}</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '130px 1fr', gap: '8px' }}>
                <span style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Learning Style:</span>
                <span style={{ color: 'var(--color-text-main)' }}>{activeLearner.learning_preference}</span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Known Skills List */}
            <div className="card">
              <div className="card-header-clean">
                <h3 className="card-title-clean">Known Skills & Credited Prereqs</h3>
              </div>
              
              {activeLearner.current_knowledge && activeLearner.current_knowledge.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
                  {activeLearner.current_knowledge.map((s, idx) => (
                    <span key={idx} className="badge badge-completed">
                      {s}
                    </span>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>No prior skills recorded.</p>
              )}
            </div>

            {/* Diagnostic Focus */}
            <div className="card">
              <div className="card-header-clean">
                <h3 className="card-title-clean">Current Focus & Diagnostics</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Current Learning Module: </span>
                  <strong>{dashboardData?.current_learning_item || 'Foundations'}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Roadmap Status: </span>
                  <span>{dashboardData?.completed_items_count || 0} stages completed</span>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Identified Weak Areas: </span>
                  {activeLearner.weak_areas && activeLearner.weak_areas.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
                      {activeLearner.weak_areas.map((w, idx) => (
                        <span key={idx} className="badge badge-remedial">
                          {w}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span style={{ color: 'var(--success-text)' }}>None. Solid comprehension.</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Edit Mode Form Layout */
        <div className="grid-2">
          {/* Calibration Details Editor */}
          <div className="card">
            <div className="card-header-clean">
              <h3 className="card-title-clean">Edit Learning Calibration</h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                    Name
                  </label>
                  <input
                    type="text"
                    className="text-input-clean"
                    style={{ width: '100%', marginTop: '4px' }}
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                    Target Goal
                  </label>
                  <input
                    type="text"
                    className="text-input-clean"
                    style={{ width: '100%', marginTop: '4px' }}
                    value={formData.target_goal}
                    onChange={(e) => setFormData({ ...formData, target_goal: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                    Direction
                  </label>
                  <select
                    className="text-input-clean"
                    style={{ width: '100%', marginTop: '4px' }}
                    value={formData.direction}
                    onChange={(e) => setFormData({ ...formData, direction: e.target.value })}
                  >
                    <option value="Cloud / DevOps">Cloud / DevOps</option>
                    <option value="Full-Stack Web">Full-Stack Web</option>
                    <option value="AI & Machine Learning">AI & Machine Learning</option>
                    <option value="Data Engineering">Data Engineering</option>
                    <option value="UI/UX Design">UI/UX Design</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                    Current Level
                  </label>
                  <select
                    className="text-input-clean"
                    style={{ width: '100%', marginTop: '4px' }}
                    value={formData.current_level}
                    onChange={(e) => setFormData({ ...formData, current_level: e.target.value })}
                  >
                    <option value="Beginner">Beginner</option>
                    <option value="Early Intermediate">Early Intermediate</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                    Available Study Time
                  </label>
                  <input
                    type="text"
                    className="text-input-clean"
                    style={{ width: '100%', marginTop: '4px' }}
                    value={formData.available_time}
                    onChange={(e) => setFormData({ ...formData, available_time: e.target.value })}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                    Target Timeline
                  </label>
                  <input
                    type="text"
                    className="text-input-clean"
                    style={{ width: '100%', marginTop: '4px' }}
                    value={formData.target_timeline}
                    onChange={(e) => setFormData({ ...formData, target_timeline: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                  Learning Style Preference
                </label>
                <select
                  className="text-input-clean"
                  style={{ width: '100%', marginTop: '4px' }}
                  value={formData.learning_preference}
                  onChange={(e) => setFormData({ ...formData, learning_preference: e.target.value })}
                >
                  <option value="Practical / Project-based">Practical / Project-based</option>
                  <option value="Visual & Interactive">Visual & Interactive</option>
                  <option value="Concept-first / Theory">Concept-first / Theory</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                <button className="btn btn-primary" onClick={() => handleSave(false)} disabled={isSaving}>
                  Save Changes
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleSave(true)}
                  disabled={isSaving}
                  title="Save and recalculate roadmap"
                >
                  <RefreshIcon size={14} />
                  <span>Save & Recalculate</span>
                </button>
                <button className="btn btn-secondary" onClick={() => setIsEditing(false)} disabled={isSaving}>
                  Cancel
                </button>
              </div>
            </div>
          </div>

          {/* Known Skills Management Editor */}
          <div className="card">
            <div className="card-header-clean">
              <div>
                <h3 className="card-title-clean">Known Skills & Credited Prereqs</h3>
                <p className="card-subtitle-clean">Topics marked as already understood</p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px', marginBottom: '14px' }}>
              <input
                type="text"
                className="text-input-clean"
                placeholder="Add prior skill (e.g. Linux, Figma, Python)..."
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
              />
              <button className="btn btn-secondary btn-sm" onClick={handleAddSkill}>
                Add
              </button>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {formData.current_knowledge.map((s, idx) => (
                <span
                  key={idx}
                  className="badge badge-completed"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                >
                  <CheckIcon size={12} />
                  <span>{s}</span>
                  <button
                    onClick={() => handleRemoveSkill(s)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#166534', fontWeight: 600 }}
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Theme Settings Zone */}
      {!isEditing && (
        <div className="card">
          <div className="card-header-clean">
            <h3 className="card-title-clean">Appearance</h3>
          </div>
          <p style={{ fontSize: '13.5px', color: 'var(--color-text-secondary)', marginBottom: '14px' }}>
            Personalize your LearnPath workspace theme.
          </p>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              className={`btn ${theme === 'light' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTheme('light')}
            >
              Light Theme
            </button>
            <button
              className={`btn ${theme === 'dark' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTheme('dark')}
            >
              Dark Theme
            </button>
          </div>
        </div>
      )}

      {/* Danger Zone */}
      {!isEditing && (
        <div className="card" style={{ border: '1px solid #fecaca', backgroundColor: 'var(--color-bg)' }}>
          <div className="card-header-clean">
            <h3 className="card-title-clean" style={{ color: '#dc2626' }}>Danger Zone</h3>
          </div>
          <p style={{ fontSize: '13.5px', color: 'var(--color-text-secondary)', marginBottom: '14px' }}>
            Permanently delete your LearnPath profile, roadmap stages, feedback, and mentor history.
          </p>
          <div>
            <button
              className="btn btn-secondary"
              style={{ borderColor: '#fca5a5', color: '#dc2626', fontWeight: 600 }}
              onClick={() => setShowDeleteModal(true)}
            >
              Delete Profile
            </button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-backdrop" style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.4)',
          backdropFilter: 'blur(3px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div className="card" style={{ maxWidth: '460px', width: '100%', gap: '16px', display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#dc2626', margin: 0 }}>Delete your profile?</h3>
            <p style={{ fontSize: '14px', lineHeight: '1.5', color: 'var(--color-text-secondary)', margin: 0 }}>
              This will permanently remove your learner profile, learning progress, roadmap, feedback, assessment history, project progress, and Mentor conversation.
            </p>
            <p style={{ fontSize: '14px', fontWeight: 600, color: '#dc2626', margin: 0 }}>
              Your account cannot be restored after deletion.
            </p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '12px' }}>
              <button className="btn btn-secondary" onClick={() => setShowDeleteModal(false)} disabled={isDeleting}>
                Cancel
              </button>
              <button
                className="btn"
                style={{ backgroundColor: '#dc2626', color: '#ffffff', fontWeight: 600 }}
                onClick={handleConfirmDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Delete Profile'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
