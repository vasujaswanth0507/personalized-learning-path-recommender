import React, { useState } from 'react';
import { useLearner } from '../context/LearnerContext';
import {
  DashboardIcon,
  RoadmapIcon,
  BookOpenIcon,
  CodeIcon,
  CheckCircleIcon,
  BotIcon,
  UserIcon,
  SettingsIcon,
  ArrowRightIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  XIcon
} from './Icons';

export default function Sidebar({
  activePage,
  setActivePage,
  isMobileOpen,
  setIsMobileOpen,
  isCollapsed,
  setIsCollapsed
}) {
  const { activeLearner, openMentorWithContext } = useLearner();

  const handleNav = (page) => {
    setActivePage(page);
    if (setIsMobileOpen) setIsMobileOpen(false);
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
    <>
      {isMobileOpen && (
        <div
          className="drawer-overlay"
          style={{ zIndex: 25 }}
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''} ${isMobileOpen ? 'mobile-open' : ''}`}>
        {/* Brand Header */}
        <div className="sidebar-header">
          <div className="sidebar-logo" onClick={() => handleNav(activeLearner ? 'dashboard' : 'onboarding')}>
            LP
          </div>
          {!isCollapsed && <span className="sidebar-brand-name">LearnPath</span>}

          {/* Desktop collapse toggle */}
          <button
            className="sidebar-collapse-btn desktop-only"
            onClick={() => setIsCollapsed(!isCollapsed)}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRightIcon size={14} /> : <ChevronLeftIcon size={14} />}
          </button>

          {/* Mobile close */}
          {isMobileOpen && (
            <button
              onClick={() => setIsMobileOpen(false)}
              className="sidebar-close-mobile mobile-only"
              aria-label="Close sidebar"
            >
              <XIcon size={18} />
            </button>
          )}
        </div>

        {/* Navigation Sections */}
        <div className="sidebar-content">
          <div>
            {!isCollapsed && <div className="sidebar-section-label">Learning Track</div>}
            <ul className="sidebar-nav-list">
              <li>
                <button
                  className={`sidebar-nav-item ${activePage === 'dashboard' ? 'active' : ''}`}
                  onClick={() => handleNav('dashboard')}
                  title="Overview"
                >
                  <DashboardIcon size={17} />
                  {!isCollapsed && <span>Overview</span>}
                </button>
              </li>
              <li>
                <button
                  className={`sidebar-nav-item ${activePage === 'path' ? 'active' : ''}`}
                  onClick={() => handleNav('path')}
                  title="My Roadmap"
                >
                  <RoadmapIcon size={17} />
                  {!isCollapsed && <span>My Roadmap</span>}
                </button>
              </li>
              <li>
                <button
                  className={`sidebar-nav-item ${activePage === 'resources' ? 'active' : ''}`}
                  onClick={() => handleNav('resources')}
                  title="Resources"
                >
                  <BookOpenIcon size={17} />
                  {!isCollapsed && <span>Resources</span>}
                </button>
              </li>
              <li>
                <button
                  className={`sidebar-nav-item ${activePage === 'projects' ? 'active' : ''}`}
                  onClick={() => handleNav('projects')}
                  title="Projects"
                >
                  <CodeIcon size={17} />
                  {!isCollapsed && <span>Projects</span>}
                </button>
              </li>
              <li>
                <button
                  className={`sidebar-nav-item ${activePage === 'assessments' ? 'active' : ''}`}
                  onClick={() => handleNav('assessments')}
                  title="Assessments"
                >
                  <CheckCircleIcon size={17} />
                  {!isCollapsed && <span>Assessments</span>}
                </button>
              </li>
            </ul>
          </div>

          <div className="sidebar-divider" />

          <div>
            {!isCollapsed && <div className="sidebar-section-label">Workspace</div>}
            <ul className="sidebar-nav-list">
              <li>
                <button
                  className={`sidebar-nav-item ${activePage === 'mentor_view' ? 'active' : ''}`}
                  onClick={() => {
                    openMentorWithContext();
                    if (setIsMobileOpen) setIsMobileOpen(false);
                  }}
                  title="Mentor"
                >
                  <BotIcon size={17} />
                  {!isCollapsed && <span>Mentor</span>}
                </button>
              </li>
              <li>
                <button
                  className={`sidebar-nav-item ${activePage === 'profile' ? 'active' : ''}`}
                  onClick={() => handleNav('profile')}
                  title="Profile"
                >
                  <UserIcon size={17} />
                  {!isCollapsed && <span>Profile</span>}
                </button>
              </li>
              <li>
                <button
                  className={`sidebar-nav-item ${activePage === 'settings' ? 'active' : ''}`}
                  onClick={() => handleNav('settings')}
                  title="Settings"
                >
                  <SettingsIcon size={17} />
                  {!isCollapsed && <span>Settings</span>}
                </button>
              </li>
              <li>
                <button
                  className={`sidebar-nav-item ${activePage === 'onboarding' ? 'active' : ''}`}
                  onClick={() => handleNav('onboarding')}
                  title="New Journey"
                >
                  <ArrowRightIcon size={17} />
                  {!isCollapsed && <span>New Journey</span>}
                </button>
              </li>
            </ul>
          </div>
        </div>

        {/* User Identity Footer */}
        {activeLearner && (
          <div
            className="sidebar-footer"
            onClick={() => handleNav('profile')}
            title={`View profile for ${activeLearner.name}`}
          >
            <div className="user-avatar-sm">{getInitials(activeLearner.name)}</div>
            {!isCollapsed && (
              <div className="user-info-text">
                <div className="user-name-label">{activeLearner.name}</div>
                <div className="user-goal-sublabel">
                  {activeLearner.target_goal || activeLearner.direction}
                </div>
              </div>
            )}
          </div>
        )}
      </aside>
    </>
  );
}
