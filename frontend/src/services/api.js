/**
 * API service for AIAlchemy platform
 * Handles all backend communication with error handling and retry logic
 */

import axios from 'axios';
import { API_CONFIG, ENV_CONFIG, logApiConfig } from '../config/api.js';

// Log current API configuration for debugging
logApiConfig();

// Create axios instance with dynamic configuration
const api = axios.create(API_CONFIG);

// Request interceptor for adding auth tokens (when implemented)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login when auth is implemented
      localStorage.removeItem('authToken');
    }
    
    return Promise.reject(error);
  }
);

// Dashboard API calls
export const dashboardApi = {
  // Get dashboard overview (fast loading)
  getOverview: () => api.get('/api/dashboard/overview'),
  
  // Get complete dashboard stats
  getStats: () => api.get('/api/dashboard/stats'),
};

// Startups API calls
export const startupsApi = {
  // Get paginated startups list with filters
  getStartups: (params = {}) => api.get('/api/startups/', { params }),
  
  // Get specific startup details
  getStartup: (id) => api.get(`/api/startups/${id}`),
  
  // Create new startup
  createStartup: (data) => api.post('/api/startups/', data),
  
  // Update startup
  updateStartup: (id, data) => api.put(`/api/startups/${id}`, data),
  
  // Search suggestions
  getSearchSuggestions: (query, limit = 5) => 
    api.get('/api/startups/search/suggestions', { params: { query, limit } }),
  
  // Get count by status
  getStatusCount: (status) => api.get(`/api/startups/status/${status}/count`),
};

// Pipeline API calls
export const pipelineApi = {
  // Get pipeline statistics
  getStats: () => api.get('/api/pipeline/stats'),
  
  // Get pipeline stages (Kanban data)
  getStages: () => api.get('/api/pipeline/stages'),
  
  // Get bottleneck analysis
  getBottlenecks: () => api.get('/api/pipeline/bottlenecks'),
  
  // Get throughput metrics
  getThroughput: (days = 30) => api.get('/api/pipeline/throughput', { params: { days } }),
  
  // Update application status
  updateStatus: (startupId, newStatus, notes = '') => 
    api.put(`/api/pipeline/applications/${startupId}/status`, newStatus, {
      params: { notes }
    }),
};

// Settings API calls
export const settingsApi = {
  // User management
  getCurrentUser: () => api.get('/api/settings/users/me'),
  updateCurrentUser: (data) => api.put('/api/settings/users/me', data),
  getAllUsers: () => api.get('/api/settings/users'),
  
  // Investment weights
  getInvestmentWeights: () => api.get('/api/settings/investment-weights'),
  updateInvestmentWeights: (data) => api.put('/api/settings/investment-weights', data),
  
  // Account preferences  
  getPreferences: () => api.get('/api/settings/account/preferences'),
  updatePreferences: (data) => api.put('/api/settings/account/preferences', data),
  
  // System configuration
  getSettings: () => api.get('/api/settings/account/preferences'), // Fallback to preferences
  updateSettings: (data) => api.put('/api/settings/account/preferences', data),
  
  // System info
  getSystemInfo: () => api.get('/api/settings/system/info'),
  getIndustries: () => api.get('/api/settings/industries'),
};

// Investment Memos API calls
export const memosApi = {
  // Get memo for startup
  getMemoByStartup: (startupId) => api.get(`/api/memos/startup/${startupId}`),
  
  // Create memo
  createMemo: (data, authorId) => api.post('/api/memos/', data, { params: { author_id: authorId } }),
  
  // Update memo
  updateMemo: (memoId, data) => api.put(`/api/memos/${memoId}`, data),
  
  // Approve memo
  approveMemo: (memoId) => api.post(`/api/memos/${memoId}/approve`),
  
  // Schedule review
  scheduleReview: (memoId, reviewDate) => 
    api.post(`/api/memos/${memoId}/schedule-review`, null, { params: { review_date: reviewDate } }),
  
  // Get memo stats
  getStats: () => api.get('/api/memos/stats/summary'),
};

// Users/Team Management API calls
export const usersApi = {
  // Get team members
  getTeamMembers: () => api.get('/api/settings/users'),
  
  // Invite new user
  inviteUser: (userData) => api.post('/api/settings/users/invite', userData),
  
  // Remove user
  removeUser: (userId) => api.delete(`/api/settings/users/${userId}`),
  
  // Update user role
  updateUserRole: (userId, role) => api.put(`/api/settings/users/${userId}/role`, { role }),
};

// File Upload API calls
export const uploadsApi = {
  // Upload files for startup
  uploadFiles: (startupId, fileType, files) => {
    const formData = new FormData();
    formData.append('file_type', fileType);
    files.forEach(file => formData.append('files', file));
    
    return api.post(`/api/uploads/startup/${startupId}/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  // Upload single file (for use during application creation)
  uploadFile: (formData, onUploadProgress) => {
    return api.post('/api/uploads/files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress
    });
  },
  
  // Get files for startup
  getStartupFiles: (startupId, fileType = null) => 
    api.get(`/api/uploads/startup/${startupId}/files`, { 
      params: fileType ? { file_type: fileType } : {} 
    }),
  
  // Download file
  downloadFile: (fileId) => api.get(`/api/uploads/files/${fileId}`, { responseType: 'blob' }),
  
  // Delete file
  deleteFile: (fileId) => api.delete(`/api/uploads/files/${fileId}`),
  
  // Get upload stats
  getStats: () => api.get('/api/uploads/stats/summary'),
};

// Utility functions
export const apiUtils = {
  // Test API connection
  testConnection: () => api.get('/health'),
  
  // Get API status
  getApiStatus: () => api.get('/api/status'),
  
  // Get current API configuration
  getApiConfig: () => ({
    baseURL: API_CONFIG.baseURL,
    environment: ENV_CONFIG.environment,
    isProduction: ENV_CONFIG.isProduction,
    timeout: API_CONFIG.timeout,
  }),
  
  // Test environment detection
  testEnvironment: () => {
    console.log('🧪 Environment Test Results:', {
      detectedEnv: ENV_CONFIG.environment,
      hostname: window.location.hostname,
      apiUrl: API_CONFIG.baseURL,
      isProduction: ENV_CONFIG.isProduction,
      isDevelopment: ENV_CONFIG.isDevelopment,
    });
    return ENV_CONFIG;
  },
  
  // Handle API errors
  handleError: (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error';
      return { success: false, message, status: error.response.status };
    } else if (error.request) {
      // Network error
      return { success: false, message: 'Network error - please check your connection', status: 0 };
    } else {
      // Other error
      return { success: false, message: error.message || 'An error occurred', status: -1 };
    }
  },
};

export default api;