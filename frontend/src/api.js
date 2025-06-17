import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API endpoints
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
};

// File API endpoints  
export const fileAPI = {
  uploadFile: (formData) => api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  listFiles: (page = 1, pageSize = 10) => {
    const skip = (page - 1) * pageSize;
    return api.get(`/upload/?skip=${skip}&limit=${pageSize}`);
  },
  getFile: (fileId) => api.get(`/upload/${fileId}`),
  deleteFile: (fileId) => api.delete(`/upload/${fileId}`),
  getFileStatus: (fileId) => api.get(`/upload/${fileId}`),
};

// Phase 3: Validation API endpoints
export const validationAPI = {
  // Template Management
  createTemplate: (templateData) => 
    api.post('/validation/templates', templateData),
  
  getTemplates: (activeOnly = true, usePublic = false) => {
    const endpoint = usePublic ? 
      `/validation/templates/public?active_only=${activeOnly}` : 
      `/validation/templates?active_only=${activeOnly}`;
    
    return api.get(endpoint).catch(error => {
      // If authentication fails and we're not using public endpoint, try public
      if ((error.response?.status === 401 || error.response?.status === 403) && !usePublic) {
        return validationAPI.getTemplates(activeOnly, true);
      }
      throw error;
    });
  },
  
  getTemplate: (templateId) => 
    api.get(`/validation/templates/${templateId}`),
  
  // Document Analysis
  analyzeDocument: (fileId) => 
    api.post(`/validation/analyze/${fileId}`),
  
  // Validation Sessions
  createValidationSession: (sessionData) => 
    api.post('/validation/sessions', sessionData),
  
  getValidationSessions: (page = 1, pageSize = 10) => {
    const skip = (page - 1) * pageSize;
    return api.get(`/validation/sessions?skip=${skip}&limit=${pageSize}`);
  },
  
  getValidationSession: (sessionId) => 
    api.get(`/validation/sessions/${sessionId}`),
  
  getSessionTerms: (sessionId) => 
    api.get(`/validation/sessions/${sessionId}/terms`),
  
  getSessionResults: (sessionId) => 
    api.get(`/validation/sessions/${sessionId}/results`),
  
  getSessionSummary: (sessionId) => 
    api.get(`/validation/sessions/${sessionId}/summary`),
};

export default api; 