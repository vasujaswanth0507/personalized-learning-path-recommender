import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api/client';

const LearnerContext = createContext(null);

export function LearnerProvider({ children }) {
  const [activeLearner, setActiveLearnerState] = useState(null);
  const [learnersList, setLearnersList] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // AI Mentor state
  const [isMentorOpen, setIsMentorOpen] = useState(false);
  const [mentorContextTopic, setMentorContextTopic] = useState('');

  // Feedback Modal state
  const [feedbackItem, setFeedbackItem] = useState(null);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  // Toast notification
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'info') => {
    setToast({ message, type, id: Date.now() });
    setTimeout(() => {
      setToast(null);
    }, 4000);
  };

  // Load existing learners
  const refreshLearners = async () => {
    try {
      const list = await api.listLearners();
      setLearnersList(list);
      
      const savedId = localStorage.getItem('learnpath_active_learner_id');
      if (savedId && list.length > 0) {
        const found = list.find((l) => l.id === parseInt(savedId, 10));
        if (found) {
          setActiveLearnerState(found);
          return found;
        }
      }
      if (list.length > 0) {
        setActiveLearnerState(list[0]);
        localStorage.setItem('learnpath_active_learner_id', list[0].id.toString());
        return list[0];
      }
    } catch (err) {
      console.error('Failed to load learners:', err);
    } finally {
      setIsLoading(false);
    }
    return null;
  };

  useEffect(() => {
    refreshLearners();
  }, []);

  const setActiveLearner = (learner) => {
    setActiveLearnerState(learner);
    if (learner) {
      localStorage.setItem('learnpath_active_learner_id', learner.id.toString());
    } else {
      localStorage.removeItem('learnpath_active_learner_id');
    }
  };

  const refreshDashboard = async () => {
    if (!activeLearner) return;
    try {
      const data = await api.getDashboard(activeLearner.id);
      setDashboardData(data);
    } catch (err) {
      console.error('Failed to refresh dashboard:', err);
    }
  };

  useEffect(() => {
    if (activeLearner) {
      refreshDashboard();
    } else {
      setDashboardData(null);
    }
  }, [activeLearner]);

  const openMentorWithContext = (topic = '') => {
    setMentorContextTopic(topic);
    setIsMentorOpen(true);
  };

  const openFeedback = (item) => {
    setFeedbackItem(item);
    setIsFeedbackOpen(true);
  };

  const closeFeedback = () => {
    setFeedbackItem(null);
    setIsFeedbackOpen(false);
  };

  return (
    <LearnerContext.Provider
      value={{
        activeLearner,
        setActiveLearner,
        learnersList,
        refreshLearners,
        dashboardData,
        refreshDashboard,
        isLoading,
        isMentorOpen,
        setIsMentorOpen,
        mentorContextTopic,
        openMentorWithContext,
        feedbackItem,
        isFeedbackOpen,
        openFeedback,
        closeFeedback,
        toast,
        showToast,
      }}
    >
      {children}
    </LearnerContext.Provider>
  );
}

export function useLearner() {
  const context = useContext(LearnerContext);
  if (!context) {
    throw new Error('useLearner must be used within a LearnerProvider');
  }
  return context;
}
