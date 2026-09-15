import React, { useState } from 'react';
import { LearnerProvider, useLearner } from './context/LearnerContext';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import AIMentorDrawer from './components/AIMentorDrawer';
import FeedbackModal from './components/FeedbackModal';

// Pages
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import LearningPathPage from './pages/LearningPathPage';
import ResourcesPage from './pages/ResourcesPage';
import ProjectsPage from './pages/ProjectsPage';
import AssessmentPage from './pages/AssessmentPage';
import ProfilePage from './pages/ProfilePage';

function MainApp() {
  const { activeLearner, toast } = useLearner();
  const [activePage, setActivePage] = useState(activeLearner ? 'dashboard' : 'onboarding');
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showStartup, setShowStartup] = useState(true);
  const [theme, setThemeState] = useState(() => {
    return localStorage.getItem('learnpath_theme') || 'dark'; // default to dark mode
  });

  const setTheme = (newTheme) => {
    setThemeState(newTheme);
    localStorage.setItem('learnpath_theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setShowStartup(false);
    }, 1200);
    return () => clearTimeout(timer);
  }, []);

  React.useEffect(() => {
    if (activeLearner && activePage === 'onboarding') {
      setActivePage('dashboard');
    }
  }, [activeLearner]);

  const renderPage = () => {
    switch (activePage) {
      case 'onboarding':
        return (
          <OnboardingPage
            onOnboardingComplete={() => setActivePage('dashboard')}
          />
        );
      case 'dashboard':
        return <DashboardPage setActivePage={setActivePage} />;
      case 'path':
        return <LearningPathPage setActivePage={setActivePage} />;
      case 'resources':
        return <ResourcesPage setActivePage={setActivePage} />;
      case 'projects':
        return <ProjectsPage setActivePage={setActivePage} />;
      case 'assessments':
        return <AssessmentPage setActivePage={setActivePage} />;
      case 'profile':
      case 'settings':
        return <ProfilePage setActivePage={setActivePage} theme={theme} setTheme={setTheme} />;
      default:
        return <DashboardPage setActivePage={setActivePage} />;
    }
  };

  if (showStartup) {
    return (
      <div className="startup-animation-screen">
        <div className="startup-wordmark-container">
          <div className="startup-logo">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--primary-700)' }}>
              <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
              <line x1="4" y1="22" x2="4" y2="15"/>
            </svg>
          </div>
          <span className="startup-brand">LearnPath</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`app-shell ${isCollapsed ? 'sidebar-is-collapsed' : ''}`}>
      {/* Left Sidebar */}
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
      />

      {/* Main Column */}
      <div className="app-main">
        <Header activePage={activePage} setActivePage={setActivePage} setIsMobileOpen={setIsMobileOpen} theme={theme} setTheme={setTheme} />

        <main className="page-content">
          {renderPage()}
        </main>
      </div>

      {/* Global Mentor Drawer */}
      <AIMentorDrawer />

      {/* Global Feedback Modal */}
      <FeedbackModal />

      {/* Toast Notice */}
      {toast && (
        <div className="toast-notice">
          <span>{toast.message}</span>
        </div>
      )}
    </div>
  );
}

export default function App() {
  return (
    <LearnerProvider>
      <MainApp />
    </LearnerProvider>
  );
}
