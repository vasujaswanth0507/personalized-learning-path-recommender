import React from 'react';
import { useLearner } from '../context/LearnerContext';

export default function Navbar({ activePage, setActivePage }) {
  const { activeLearner, openMentorWithContext } = useLearner();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'path', label: 'My Roadmap', icon: '🗺️' },
    { id: 'resources', label: 'Resources', icon: '📚' },
    { id: 'projects', label: 'Projects', icon: '🛠️' },
    { id: 'assessments', label: 'Assessments', icon: '📝' },
    { id: 'profile', label: 'Profile', icon: '👤' },
  ];

  return (
    <nav className="navbar">
      <div className="nav-inner">
        {/* Brand */}
        <div className="brand-wrapper" onClick={() => setActivePage('dashboard')}>
          <div className="brand-icon">LP</div>
          <div>
            <div className="brand-title">LearnPath</div>
            <span className="brand-badge">Intelligent Learning Mentor</span>
          </div>
        </div>

        {/* Nav Links */}
        <ul className="nav-links">
          {navItems.map((item) => (
            <li key={item.id}>
              <button
                className={`nav-link-btn ${activePage === item.id ? 'active' : ''}`}
                onClick={() => setActivePage(item.id)}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            </li>
          ))}
        </ul>

        {/* Actions */}
        <div className="nav-actions">
          {activeLearner && (
            <button
              className="btn btn-mentor-trigger"
              onClick={() => openMentorWithContext()}
            >
              <span>🤖</span>
              <span>AI Mentor</span>
            </button>
          )}

          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setActivePage('onboarding')}
            title="Start a new learning journey"
          >
            <span>✨</span>
            <span>New Journey</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
