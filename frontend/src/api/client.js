const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Onboarding
  onboardingChat: (message, history = [], current_extracted = {}) =>
    request('/onboarding/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history, current_extracted }),
    }),

  // Profile
  createProfile: (data) =>
    request('/profile', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getLearner: (id) => request(`/profile/${id}`),
  listLearners: () => request('/profile'),
  updateProfile: (id, data, regenerate = false) =>
    request(`/profile/${id}?regenerate_path=${regenerate}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  deleteProfile: (id) =>
    request(`/profile/${id}`, {
      method: 'DELETE',
    }),

  // Paths
  getPath: (learnerId) => request(`/paths/${learnerId}`),
  regeneratePath: (learnerId) =>
    request(`/paths/${learnerId}/generate`, { method: 'POST' }),
  updatePathItemStatus: (itemId, status) =>
    request(`/paths/items/${itemId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  // Resources
  getResources: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/resources${q ? `?${q}` : ''}`);
  },
  getResource: (id, learnerId) =>
    request(`/resources/${id}${learnerId ? `?learner_id=${learnerId}` : ''}`),
  updateResourceProgress: (resourceId, learnerId, data) =>
    request(`/resources/${resourceId}/progress?learner_id=${learnerId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Projects
  getProjects: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/projects${q ? `?${q}` : ''}`);
  },
  getProject: (id, learnerId) =>
    request(`/projects/${id}${learnerId ? `?learner_id=${learnerId}` : ''}`),
  updateProjectProgress: (projectId, learnerId, data) =>
    request(`/projects/${projectId}/progress?learner_id=${learnerId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Assessments
  getAssessments: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/assessments${q ? `?${q}` : ''}`);
  },
  getAssessment: (id) => request(`/assessments/${id}`),
  submitAssessment: (assessmentId, learnerId, answers) =>
    request(`/assessments/${assessmentId}/submit?learner_id=${learnerId}`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    }),

  // Feedback
  submitFeedback: (learnerId, data) =>
    request(`/feedback?learner_id=${learnerId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getFeedback: (learnerId) => request(`/feedback/${learnerId}`),

  // Mentor
  askMentor: (learnerId, message, currentStage = '', contextTopic = '') =>
    request(`/mentor/${learnerId}/chat`, {
      method: 'POST',
      body: JSON.stringify({
        message,
        current_stage: currentStage,
        context_topic: contextTopic,
      }),
    }),
  getMentorHistory: (learnerId) => request(`/mentor/${learnerId}/history`),

  // Dashboard
  getDashboard: (learnerId) => request(`/dashboard/${learnerId}`),
};
