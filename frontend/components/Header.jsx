import React from 'react';
import { useLearner } from '../context/LearnerContext';
import { MenuIcon, BotIcon } from './Icons';

export default function Header({ activePage, setActivePage, setIsMobileOpen, theme, setTheme }) {
  const { activeLearner, openMentorWithContext } = useLearner();

  const getPageTitle = () => {
    switch (activePage) {
      case 'dashboard':
        return 'Overview';
      case 'path':
        return 'My Learning Roadmap';
      case 'resources':
        return 'Learning Resources';
      case 'projects':
        return 'Practical Projects';
      case 'assessments':
        return 'Skill Assessments';
      case 'profile':
        return 'Learner Profile';
      case 'onboarding':
        return 'Start New Journey';
      default:
        return 'Overview';
    }
  };

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
    <header className="top-header">
      <div className="header-left">
        <button
          className="mobile-menu-toggle"
          onClick={() => setIsMobileOpen(true)}
          aria-label="Toggle navigation menu"
        >
          <MenuIcon size={20} />
        </button>
        <h1 className="page-header-title">{getPageTitle()}</h1>
      </div>

      <div className="header-right">
        {/* Theme Switcher Toggle */}
        <button
          className="btn btn-secondary btn-icon-only"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
          style={{ width: '32px', height: '32px', padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          {theme === 'dark' ? (
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="4"/>
              <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
              <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
            </svg>
          )}
        </button>

        {/* Mentor Trigger */}
        {activeLearner && activePage !== 'onboarding' && (
          <button
            className="btn btn-secondary btn-sm header-mentor-btn"
            onClick={() => openMentorWithContext()}
            title="Ask your Mentor"
          >
            <BotIcon size={16} />
            <span>Mentor</span>
          </button>
        )}

        {/* Profile Access Control */}
        {activeLearner ? (
          <div 
            className="header-profile-control"
            onClick={() => setActivePage('profile')}
            title="Go to Learner Profile"
          >
            <span className="header-username desktop-only">{activeLearner.name}</span>
            <div className="header-avatar">
              {getInitials(activeLearner.name)}
            </div>
          </div>
        ) : (
          activePage !== 'onboarding' && (
            <button 
              className="btn btn-primary btn-sm"
              onClick={() => setActivePage('onboarding')}
            >
              Get Started
            </button>
          )
        )}
      </div>
    </header>
  );
}
