/**
 * API service for AIAlchemy platform
 * Handles all backend communication with error handling and retry logic
 */

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL ? 
    `${process.env.REACT_APP_API_BASE_URL}/api` : 
    '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
  async (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Unauthorized - try to refresh token
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken && !error.config._retry) {
        error.config._retry = true;
        
        try {
          const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
          const { access_token } = response.data;
          
          localStorage.setItem('authToken', access_token);
          error.config.headers.Authorization = `Bearer ${access_token}`;
          
          return api(error.config);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('authToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
        }
      } else {
        // No refresh token or refresh failed
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Authentication API calls
export const authApi = {
  // User login
  login: (credentials) => api.post('/auth/login', credentials),
  
  // User registration
  register: (userData) => api.post('/auth/register', userData),
  
  // User logout
  logout: () => api.post('/auth/logout'),
  
  // Refresh JWT token
  refreshToken: (tokenData) => api.post('/auth/refresh', tokenData),
  
  // Get current user profile
  getCurrentUser: () => api.get('/auth/me'),
  
  // Update user profile
  updateProfile: (profileData) => api.put('/auth/me', profileData),
};

// Dashboard API calls
export const dashboardApi = {
  // Get dashboard overview (fast loading)
  getOverview: () => api.get('/dashboard/overview'),
  
  // Get complete dashboard stats
  getStats: () => api.get('/dashboard/stats'),
};

// Startups API calls
export const startupsApi = {
  // Get paginated startups list with filters
  getStartups: (params = {}) => api.get('/startups/', { params }),
  
  // Get specific startup details
  getStartup: (id) => api.get(`/startups/${id}`),
  
  // Create new startup
  createStartup: (data) => api.post('/startups/', data),
  
  // Update startup
  updateStartup: (id, data) => api.put(`/startups/${id}`, data),
  
  // Search suggestions
  getSearchSuggestions: (query, limit = 5) => 
    api.get('/startups/search/suggestions', { params: { query, limit } }),
  
  // Get count by status
  getStatusCount: (status) => api.get(`/startups/status/${status}/count`),
};

// Pipeline API calls
export const pipelineApi = {
  // Get pipeline statistics
  getStats: () => api.get('/pipeline/stats'),
  
  // Get pipeline stages (Kanban data)
  getStages: () => api.get('/pipeline/stages'),
  
  // Get bottleneck analysis
  getBottlenecks: () => api.get('/pipeline/bottlenecks'),
  
  // Get throughput metrics
  getThroughput: (days = 30) => api.get('/pipeline/throughput', { params: { days } }),
  
  // Update application status
  updateStatus: (startupId, newStatus, notes = '') => 
    api.put(`/pipeline/applications/${startupId}/status`, newStatus, {
      params: { notes }
    }),
};

// Settings API calls
export const settingsApi = {
  // User management
  getCurrentUser: () => api.get('/settings/users/me'),
  updateCurrentUser: (data) => api.put('/settings/users/me', data),
  getAllUsers: () => api.get('/settings/users'),
  
  // Investment weights
  getInvestmentWeights: () => api.get('/settings/investment-weights'),
  updateInvestmentWeights: (data) => api.put('/settings/investment-weights', data),
  
  // Account preferences  
  getPreferences: () => api.get('/settings/account/preferences'),
  updatePreferences: (data) => api.put('/settings/account/preferences', data),
  
  // System configuration
  getSettings: () => api.get('/settings/account/preferences'), // Fallback to preferences
  updateSettings: (data) => api.put('/settings/account/preferences', data),
  
  // System info
  getSystemInfo: () => api.get('/settings/system/info'),
  getIndustries: () => api.get('/settings/industries'),
};

// Investment Memos API calls
export const memosApi = {
  // Get memo for startup
  getMemoByStartup: (startupId) => api.get(`/memos/startup/${startupId}`),
  
  // Create memo
  createMemo: (data, authorId) => api.post('/memos/', data, { params: { author_id: authorId } }),
  
  // Update memo
  updateMemo: (memoId, data) => api.put(`/memos/${memoId}`, data),
  
  // Approve memo
  approveMemo: (memoId) => api.post(`/memos/${memoId}/approve`),
  
  // Schedule review
  scheduleReview: (memoId, reviewDate) => 
    api.post(`/memos/${memoId}/schedule-review`, null, { params: { review_date: reviewDate } }),
  
  // Get memo stats
  getStats: () => api.get('/memos/stats/summary'),
};

// Users/Team Management API calls
export const usersApi = {
  // Get team members
  getTeamMembers: () => api.get('/settings/users'),
  
  // Invite new user
  inviteUser: (userData) => api.post('/settings/users/invite', userData),
  
  // Remove user
  removeUser: (userId) => api.delete(`/settings/users/${userId}`),
  
  // Update user role
  updateUserRole: (userId, role) => api.put(`/settings/users/${userId}/role`, { role }),
};

// File Upload API calls
export const uploadsApi = {
  // Upload files for startup
  uploadFiles: (startupId, fileType, files) => {
    const formData = new FormData();
    formData.append('file_type', fileType);
    files.forEach(file => formData.append('files', file));
    
    return api.post(`/uploads/startup/${startupId}/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  // Upload single file (for use during application creation)
  uploadFile: (formData, onUploadProgress) => {
    return api.post('/uploads/files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress
    });
  },
  
  // Get files for startup
  getStartupFiles: (startupId, fileType = null) => 
    api.get(`/uploads/startup/${startupId}/files`, { 
      params: fileType ? { file_type: fileType } : {} 
    }),
  
  // Download file
  downloadFile: (fileId) => api.get(`/uploads/files/${fileId}`, { responseType: 'blob' }),
  
  // Delete file
  deleteFile: (fileId) => api.delete(`/uploads/files/${fileId}`),
  
  // Get upload stats
  getStats: () => api.get('/uploads/stats/summary'),
};

// Utility functions
export const apiUtils = {
  // Test API connection
  testConnection: () => api.get('/health'),
  
  // Get API status
  getApiStatus: () => api.get('/status'),
  
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