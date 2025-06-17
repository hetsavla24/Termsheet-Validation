import axios from 'axios';
import toast from 'react-hot-toast';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-storage');
    if (token) {
      try {
        const parsedData = JSON.parse(token);
        if (parsedData.state?.token) {
          config.headers.Authorization = `Bearer ${parsedData.state.token}`;
        }
      } catch (error) {
        console.error('Error parsing auth token:', error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors
    if (!error.response) {
      toast.error('Network error. Please check if the server is running.');
      return Promise.reject(error);
    }
    
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
      toast.error('Session expired. Please login again.');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail);
    } else if (error.message) {
      toast.error(error.message);
    }
    return Promise.reject(error);
  }
);

// Authentication API methods
export const authAPI = {
  register: async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },

  login: async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  logout: async () => {
    try {
      const response = await api.post('/auth/logout');
      return response.data;
    } catch (error) {
      console.error('Logout error:', error);
      // Don't throw error for logout to allow local cleanup
      return { message: 'Logged out locally' };
    }
  },

  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  },

  updateProfile: async (userData) => {
    try {
      const response = await api.put('/auth/me', userData);
      return response.data;
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  },
};

// File Upload API methods (Phase 2)
export const fileAPI = {
  uploadFile: async (file, onUploadProgress) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: onUploadProgress,
      });
      return response.data;
    } catch (error) {
      console.error('File upload error:', error);
      throw error;
    }
  },

  getFiles: async (page = 1, pageSize = 10) => {
    try {
      const skip = (page - 1) * pageSize;
      const response = await api.get(`/upload/?skip=${skip}&limit=${pageSize}`);
      return response.data;
    } catch (error) {
      console.error('Get files error:', error);
      throw error;
    }
  },

  getFileInfo: async (fileId) => {
    try {
      const response = await api.get(`/upload/${fileId}`);
      return response.data;
    } catch (error) {
      console.error('Get file info error:', error);
      throw error;
    }
  },

  getProcessingStatus: async (fileId) => {
    try {
      const response = await api.get(`/upload/${fileId}`);
      return response.data;
    } catch (error) {
      console.error('Get processing status error:', error);
      throw error;
    }
  },

  downloadFile: async (fileId) => {
    try {
      const response = await api.get(`/upload/${fileId}/download`, {
        responseType: 'blob',
      });
      return response;
    } catch (error) {
      console.error('Download file error:', error);
      throw error;
    }
  },

  deleteFile: async (fileId) => {
    try {
      const response = await api.delete(`/upload/${fileId}`);
      return response.data;
    } catch (error) {
      console.error('Delete file error:', error);
      throw error;
    }
  },

  processFile: async (fileId) => {
    try {
      const response = await api.post(`/upload/${fileId}/process`);
      return response.data;
    } catch (error) {
      console.error('Process file error:', error);
      throw error;
    }
  },
};

// Validation API methods
export const validationAPI = {
  // Get validation system status
  getStatus: async () => {
    try {
      const response = await api.get('/validation/status');
      return response.data;
    } catch (error) {
      console.error('Get validation status error:', error);
      throw error;
    }
  },

  // Template management
  getTemplates: async (activeOnly = true, usePublic = false) => {
    const endpoint = usePublic ? 
      `/validation/templates/public?active_only=${activeOnly}` : 
      `/validation/templates?active_only=${activeOnly}`;
    
    try {
      const response = await api.get(endpoint);
      return response.data;
    } catch (error) {
      // If authentication fails and we're not using public endpoint, try public
      if (error.response?.status === 401 || error.response?.status === 403) {
        if (!usePublic) {
          return await validationAPI.getTemplates(activeOnly, true);
        }
      }
      console.error('Get templates error:', error);
      throw error;
    }
  },

  createTemplate: async (templateData) => {
    try {
      const response = await api.post('/validation/templates', templateData);
      return response.data;
    } catch (error) {
      console.error('Create template error:', error);
      throw error;
    }
  },

  // Session management
  getValidationSessions: async (page = 1, pageSize = 10) => {
    try {
      const skip = (page - 1) * pageSize;
      const response = await api.get(`/validation/sessions?skip=${skip}&limit=${pageSize}`);
      return response.data;
    } catch (error) {
      console.error('Get validation sessions error:', error);
      throw error;
    }
  },

  getValidationSession: async (sessionId) => {
    try {
      const response = await api.get(`/validation/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Get validation session error:', error);
      throw error;
    }
  },

  createValidationSession: async (sessionData) => {
    try {
      const response = await api.post('/validation/sessions', sessionData);
      return response.data;
    } catch (error) {
      console.error('Create validation session error:', error);
      throw error;
    }
  },

  // Auto-create session
  autoCreateValidationSession: async (tradeId, sessionName = null) => {
    try {
      const response = await api.post('/validation/sessions/auto-create', null, {
        params: { trade_id: tradeId, session_name: sessionName }
      });
      return response.data;
    } catch (error) {
      console.error('Auto create validation session error:', error);
      throw error;
    }
  },

  // Legacy methods for compatibility
  validateTermsheet: async (sessionId) => {
    const response = await api.post(`/validation/validate/${sessionId}`);
    return response.data;
  },

  getValidationResults: async (sessionId) => {
    const response = await api.get(`/validation/results/${sessionId}`);
    return response.data;
  },

  downloadReport: async (sessionId, format) => {
    const response = await api.get(`/validation/report/${sessionId}/${format}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Enhanced Validation Interface methods
  
  // Trade Record management
  createTradeRecord: async (tradeData) => {
    const response = await api.post('/validation/trade-records', tradeData);
    return response.data;
  },

  getTradeRecord: async (tradeId) => {
    const response = await api.get(`/validation/trade-records/${tradeId}`);
    return response.data;
  },

  listTradeRecords: async (skip = 0, limit = 50, statusFilter = null) => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString()
    });
    
    if (statusFilter) {
      params.append('status_filter', statusFilter);
    }
    
    const response = await api.get(`/validation/trade-records?${params}`);
    return response.data;
  },

  // Validation Interface specific methods
  startValidationInterface: async (sessionId, requestData) => {
    const response = await api.post(`/validation/sessions/${sessionId}/start-validation`, requestData);
    return response.data;
  },

  getValidationInterfaceData: async (sessionId) => {
    try {
      const response = await api.get(`/validation/sessions/${sessionId}/interface-data`);
      return response.data;
    } catch (error) {
      console.warn('Error getting validation interface data, trying basic interface fallback:', error);
      // Try the basic interface endpoint as fallback
      try {
        const fallbackResponse = await api.get(`/validation/sessions/${sessionId}/basic-interface`);
        return fallbackResponse.data;
      } catch (fallbackError) {
        console.error('Both interface endpoints failed:', fallbackError);
        throw fallbackError;
      }
    }
  },

  makeValidationDecision: async (sessionId, decisionData) => {
    try {
      const response = await api.post(`/validation/sessions/${sessionId}/decision`, decisionData);
      return response.data;
    } catch (error) {
      console.error('Make validation decision error:', error);
      throw error;
    }
  },
  
  updateSessionStatus: async (sessionId, statusData) => {
    try {
      const response = await api.patch(`/validation/sessions/${sessionId}/status`, statusData);
      return response.data;
    } catch (error) {
      console.error('Update session status error:', error);
      throw error;
    }
  },

  // Session terms and results for compatibility
  getSessionTerms: async (sessionId) => {
    const response = await api.get(`/validation/sessions/${sessionId}/terms`);
    return response.data;
  },

  getSessionResults: async (sessionId) => {
    const response = await api.get(`/validation/sessions/${sessionId}/results`);
    return response.data;
  },

  getSessionSummary: async (sessionId) => {
    const response = await api.get(`/validation/sessions/${sessionId}/summary`);
    return response.data;
  },

  // List method for consistency (alias for existing method)
  listFiles: async (page = 1, pageSize = 10) => {
    return await fileAPI.getFiles(page, pageSize);
  }
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api; 