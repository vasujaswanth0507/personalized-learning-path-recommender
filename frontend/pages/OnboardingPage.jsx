import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api/client';
import { useLearner } from '../context/LearnerContext';
import { ArrowRightIcon, UserIcon, XIcon, CheckCircleIcon, BotIcon } from '../components/Icons';
import MarkdownRenderer from '../components/MarkdownRenderer';

export default function OnboardingPage({ onOnboardingComplete }) {
  const { setActiveLearner, refreshLearners, showToast } = useLearner();

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Welcome to LearnPath. Tell me what's on your mind—what are you hoping to learn or achieve?",
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [history, setHistory] = useState([]);
  const [profile, setProfile] = useState({
    name: 'Learner',
    target_goal: '',
    direction: '',
    current_knowledge: [],
    current_level: 'Beginner',
    available_time: '1–2 hours daily',
    target_timeline: '3 months',
    learning_preference: 'Practical / Project-based',
    weak_areas: [],
    areas_to_explore: [],
    notes: '',
  });

  const [suggestedPrompts, setSuggestedPrompts] = useState([
    'I want to learn UI and UX',
    'I want to become a cloud engineer',
    "I'm exploring programming and design",
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isReady, setIsReady] = useState(false);

  // Profile Drawer State
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isEditingProfile, setIsEditingProfile] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const sendingRef = useRef(false);

  // Re-scroll stream on content change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Load existing onboarding draft from SQLite on mount
  const restoreOnboarding = async (id) => {
    setIsLoading(true);
    try {
      const historyList = await api.getMentorHistory(id);
      const profileData = await api.getLearner(id);

      if (historyList && historyList.length > 0) {
        const mappedMessages = historyList.map((m) => ({
          role: m.sender === 'user' ? 'user' : 'assistant',
          content: m.content,
        }));
        setMessages(mappedMessages);
        setHistory(mappedMessages);
      }

      if (profileData) {
        setProfile(profileData);
        let isReadyState = false;
        try {
          const notesData = JSON.parse(profileData.notes);
          if (notesData && notesData.onboarding_state === 'ready') {
            isReadyState = true;
          }
        } catch (e) {}
        setIsReady(isReadyState);
      }
    } catch (e) {
      console.error('Failed to restore onboarding session:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const savedId = localStorage.getItem('learnpath_onboarding_learner_id');
    if (savedId) {
      restoreOnboarding(parseInt(savedId, 10));
    }
  }, []);

  const handleSend = async (textToSend) => {
    // 1. Double submit protection check
    if (sendingRef.current) return;
    const query = textToSend || inputText;
    if (!query.trim()) return;

    sendingRef.current = true;
    setInputText('');
    setIsLoading(true);

    // Append user message to list
    const newMessages = [...messages, { role: 'user', content: query }];
    setMessages(newMessages);

    try {
      const historyPayload = history.concat([{ role: 'user', content: query }]);
      const res = await api.onboardingChat(query, historyPayload, profile);

      // Append mentor response once
      setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }]);
      setHistory(historyPayload.concat([{ role: 'assistant', content: res.reply }]));

      if (res.extracted_profile) {
        setProfile(res.extracted_profile);
        if (res.extracted_profile.id) {
          localStorage.setItem('learnpath_onboarding_learner_id', res.extracted_profile.id.toString());
        }
      }
      if (res.is_ready_for_profile !== undefined) {
        setIsReady(res.is_ready_for_profile);
      }
      if (res.suggested_chips) {
        setSuggestedPrompts(res.suggested_chips);
      }
    } catch (err) {
      console.error('Onboarding turn error:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Got it. I have noted your update in your learning profile.',
        },
      ]);
    } finally {
      setIsLoading(false);
      sendingRef.current = false;
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleGenerateRoadmap = async () => {
    setIsCreating(true);
    try {
      const learnerPayload = {
        name: profile.name || 'Learner',
        target_goal: profile.target_goal || 'Personalized Track',
        direction: profile.direction || 'UI/UX Design',
        current_knowledge: profile.current_knowledge || [],
        current_level: profile.current_level || 'Beginner',
        available_time: profile.available_time || '1-2 hours daily',
        target_timeline: profile.target_timeline || '3 months',
        learning_preference: profile.learning_preference || 'Practical / Project-based',
        weak_areas: profile.weak_areas || [],
        areas_to_explore: profile.areas_to_explore || [],
        notes: profile.notes || '',
      };

      let finalLearner;
      if (profile.id) {
        // Finalize the draft learner
        finalLearner = await api.updateProfile(profile.id, learnerPayload, true);
      } else {
        // Fallback create
        finalLearner = await api.createProfile(learnerPayload);
      }

      localStorage.removeItem('learnpath_onboarding_learner_id');
      await refreshLearners();
      setActiveLearner(finalLearner);
      showToast('Your personalized learning workspace is ready', 'success');

      if (onOnboardingComplete) {
        onOnboardingComplete(finalLearner);
      }
    } catch (err) {
      showToast('Error creating profile: ' + err.message, 'error');
    } finally {
      setIsCreating(false);
    }
  };

  const closeProfile = () => {
    setIsProfileOpen(false);
    setIsEditingProfile(false);
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const hasGoal = Boolean(profile.target_goal);
  const knownSummary =
    profile.current_knowledge?.length > 0
      ? profile.current_knowledge.slice(0, 3).join(' · ')
      : 'None';

  return (
    <div className="onboarding-workspace">
      {/* Workspace Header */}
      <header className="onboarding-header">
        <div className="onboarding-header-brand">
          <span className="onboarding-badge-tag">LearnPath Onboarding</span>
          <h1 className="onboarding-hero-title">Start Your Learning Journey</h1>
          <p className="onboarding-hero-subtitle">
            Tell me what you're trying to learn. I'll help shape the path around your starting point.
          </p>
        </div>

        {/* Live profile snapshot panel button */}
        <div className="onboarding-snapshot-bar">
          <div className="profile-snapshot-pill" onClick={() => setIsProfileOpen(true)}>
            <div className="snapshot-dot" style={{ backgroundColor: hasGoal ? 'var(--primary-600)' : 'var(--color-border)' }} />
            <div className="snapshot-details">
              <span className="snapshot-label">Goal:</span>
              <strong className="snapshot-value">{profile.target_goal || 'Exploring'}</strong>
              <span className="snapshot-sep">·</span>
              <span className="snapshot-label">Track:</span>
              <span className="snapshot-value">{profile.direction || 'Not chosen'}</span>
              <span className="snapshot-sep">·</span>
              <span className="snapshot-label">Skills:</span>
              <span className="snapshot-value">{knownSummary}</span>
            </div>
          </div>

          <button
            className="btn-profile-toggle"
            onClick={() => setIsProfileOpen(true)}
            title="Open your learning profile"
          >
            <UserIcon size={15} />
            <span>Profile Summary</span>
          </button>
        </div>
      </header>

      {/* Main Conversational Board */}
      <div className="onboarding-chat-container">
        <div className="onboarding-chat-stream">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`workspace-bubble-wrapper ${
                m.role === 'user' ? 'workspace-bubble-user' : 'workspace-bubble-mentor'
              }`}
            >
              {m.role === 'assistant' && (
                <div className="workspace-mentor-avatar">
                  <BotIcon size={16} />
                </div>
              )}
              <div className="workspace-bubble-content">
                {m.role === 'assistant' && <div className="bubble-sender-label">LearnPath Mentor</div>}
                <MarkdownRenderer content={m.content} />
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="workspace-bubble-wrapper workspace-bubble-mentor">
              <div className="workspace-mentor-avatar">
                <BotIcon size={16} />
              </div>
              <div className="workspace-bubble-content workspace-bubble-loading">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span style={{ marginLeft: '10px', color: 'var(--color-text-muted)', fontSize: '13px' }}>
                  Mentor is thinking...
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Action button if ready to generate roadmap */}
        {isReady && hasGoal && (
          <div className="onboarding-ready-banner">
            <div className="ready-banner-info">
              <CheckCircleIcon size={18} className="text-primary" />
              <span>
                Your personalized path for <strong>{profile.target_goal}</strong> is ready.
              </span>
            </div>
            <button
              className="btn btn-primary"
              onClick={handleGenerateRoadmap}
              disabled={isCreating}
              style={{ padding: '8px 18px' }}
            >
              <span>{isCreating ? 'Generating...' : 'Generate Roadmap →'}</span>
            </button>
          </div>
        )}

        {/* Suggestion Chips */}
        {suggestedPrompts && suggestedPrompts.length > 0 && (
          <div className="workspace-suggestions-row">
            {suggestedPrompts.map((p, idx) => (
              <button
                key={idx}
                className="workspace-chip"
                onClick={() => handleSend(p)}
                disabled={isLoading}
              >
                {p}
              </button>
            ))}
          </div>
        )}

        {/* Input container */}
        <div className="workspace-input-wrapper">
          <textarea
            ref={inputRef}
            className="workspace-input-field"
            placeholder="Type your response..."
            value={inputText}
            rows={1}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={isLoading}
          />
          <button
            className="workspace-send-button"
            onClick={() => handleSend()}
            disabled={!inputText.trim() || isLoading}
            aria-label="Send message"
          >
            <ArrowRightIcon size={16} />
          </button>
        </div>
      </div>

      {/* Drawer Overlay (Slide-Over panel on desktop, full sheet on mobile) */}
      {isProfileOpen && (
        <div className="profile-drawer-overlay" onClick={closeProfile}>
          <div
            className="profile-drawer-container"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-label="Your Learning Profile"
          >
            {/* Header */}
            <div className="profile-drawer-header">
              <div>
                <span className="profile-drawer-tag">YOUR PROFILE</span>
                <h3 className="profile-drawer-title">
                  {profile.target_goal || 'Details Summary'}
                </h3>
              </div>
              <button
                className="profile-drawer-close"
                onClick={closeProfile}
                aria-label="Close profile panel"
              >
                <XIcon size={18} />
              </button>
            </div>

            {/* Content */}
            <div className="profile-drawer-body">
              {!isEditingProfile ? (
                <div className="profile-summary-card">
                  <div className="profile-summary-section">
                    <span className="summary-label">Goal Target</span>
                    <div className="summary-value-strong">
                      {profile.target_goal || 'Goal not set'}
                    </div>
                  </div>

                  <div className="profile-summary-grid">
                    <div className="profile-summary-section">
                      <span className="summary-label">Track Domain</span>
                      <div className="summary-badge">{profile.direction || 'Not resolved'}</div>
                    </div>

                    <div className="profile-summary-section">
                      <span className="summary-label">Experience</span>
                      <div className="summary-badge">{profile.current_level}</div>
                    </div>
                  </div>

                  <div className="profile-summary-section">
                    <span className="summary-label">Known & Credited Skills</span>
                    {profile.current_knowledge && profile.current_knowledge.length > 0 ? (
                      <div className="summary-tags-wrap">
                        {profile.current_knowledge.map((k, i) => (
                          <span key={i} className="summary-tag summary-tag-known">
                            ✓ {k}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="summary-empty-note">
                        Starting from ground zero
                      </p>
                    )}
                  </div>

                  <div className="profile-summary-grid">
                    <div className="profile-summary-section">
                      <span className="summary-label">Study Commitment</span>
                      <div className="summary-text-val">{profile.available_time}</div>
                    </div>

                    <div className="profile-summary-section">
                      <span className="summary-label">Timeline Target</span>
                      <div className="summary-text-val">{profile.target_timeline}</div>
                    </div>
                  </div>

                  <div className="profile-summary-section">
                    <span className="summary-label">Learning Preference</span>
                    <div className="summary-text-val">{profile.learning_preference}</div>
                  </div>

                  <div style={{ marginTop: '24px' }}>
                    <button
                      className="btn btn-outline"
                      style={{ width: '100%' }}
                      onClick={() => setIsEditingProfile(true)}
                    >
                      Edit Profile Options
                    </button>
                  </div>
                </div>
              ) : (
                <div className="profile-edit-card">
                  <div className="edit-form-group">
                    <label className="edit-label">Target Goal</label>
                    <input
                      type="text"
                      className="text-input-clean"
                      value={profile.target_goal}
                      placeholder="e.g. UI/UX Design"
                      onChange={(e) => setProfile({ ...profile, target_goal: e.target.value })}
                    />
                  </div>

                  <div className="profile-summary-grid">
                    <div className="edit-form-group">
                      <label className="edit-label">Track</label>
                      <select
                        className="text-input-clean"
                        value={profile.direction}
                        onChange={(e) => setProfile({ ...profile, direction: e.target.value })}
                      >
                        <option value="">Exploring / Unsure</option>
                        <option value="UI/UX Design">UI/UX Design</option>
                        <option value="Cloud / DevOps">Cloud / DevOps</option>
                        <option value="Full-Stack Web">Full-Stack Web</option>
                        <option value="AI & Machine Learning">AI & Machine Learning</option>
                        <option value="Data Engineering">Data Engineering</option>
                      </select>
                    </div>

                    <div className="edit-form-group">
                      <label className="edit-label">Level</label>
                      <select
                        className="text-input-clean"
                        value={profile.current_level}
                        onChange={(e) => setProfile({ ...profile, current_level: e.target.value })}
                      >
                        <option value="Beginner">Beginner</option>
                        <option value="Early Intermediate">Early Intermediate</option>
                        <option value="Intermediate">Intermediate</option>
                        <option value="Advanced">Advanced</option>
                      </select>
                    </div>
                  </div>

                  <div className="profile-summary-grid">
                    <div className="edit-form-group">
                      <label className="edit-label">Daily Availability</label>
                      <input
                        type="text"
                        className="text-input-clean"
                        value={profile.available_time}
                        onChange={(e) => setProfile({ ...profile, available_time: e.target.value })}
                      />
                    </div>

                    <div className="edit-form-group">
                      <label className="edit-label">Timeline Target</label>
                      <input
                        type="text"
                        className="text-input-clean"
                        value={profile.target_timeline}
                        onChange={(e) => setProfile({ ...profile, target_timeline: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="edit-form-group">
                    <label className="edit-label">Learning Preference</label>
                    <select
                      className="text-input-clean"
                      value={profile.learning_preference}
                      onChange={(e) => setProfile({ ...profile, learning_preference: e.target.value })}
                    >
                      <option value="Practical / Project-based">Practical / Project-based</option>
                      <option value="Visual & Interactive">Visual & Interactive</option>
                      <option value="Concept-first / Theory">Concept-first / Theory</option>
                    </select>
                  </div>

                  <div style={{ marginTop: '24px', display: 'flex', gap: '10px' }}>
                    <button
                      className="btn btn-primary"
                      style={{ flex: 1 }}
                      onClick={() => setIsEditingProfile(false)}
                    >
                      Apply Changes
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Generate roadmap trigger inside panel */}
            <div className="profile-drawer-footer">
              <button
                className="btn btn-primary"
                style={{ width: '100%', padding: '12px' }}
                onClick={handleGenerateRoadmap}
                disabled={isCreating}
              >
                <span>{isCreating ? 'Generating Workspace...' : 'Generate Roadmap'}</span>
                <ArrowRightIcon size={15} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
