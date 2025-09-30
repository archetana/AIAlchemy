/**
 * Dynamic API Configuration for AIAlchemy
 * Automatically detects environment and sets appropriate API base URL
 */

// Dynamic API configuration based on environment
const getApiBaseUrl = () => {
  // Check if we're in a production environment (not localhost)
  const isProduction = window.location.hostname !== 'localhost' && 
                      window.location.hostname !== '127.0.0.1' && 
                      !window.location.hostname.includes('gitpod') &&
                      !window.location.hostname.includes('codespaces');

  if (isProduction) {
    // In production, API calls go through the same domain (API Gateway routing)
    return `${window.location.protocol}//${window.location.host}`;
  }
  
  // Development environments
  if (window.location.hostname.includes('gitpod')) {
    // GitPod environment - use port 8000 on same domain
    const port = window.location.port || '3000';
    const backendPort = port === '3000' ? '8000' : '8000';
    return `${window.location.protocol}//${window.location.hostname.replace(/^\d+-/, `${backendPort}-`)}`;
  }
  
  if (window.location.hostname.includes('codespaces')) {
    // GitHub Codespaces - use port 8000 on same domain
    return `${window.location.protocol}//${window.location.hostname.replace(/-3000/, '-8000')}`;
  }
  
  // Local development fallback
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
};

// Environment detection
export const getEnvironment = () => {
  if (process.env.NODE_ENV === 'production') {
    return 'production';
  }
  
  if (window.location.hostname.includes('gitpod')) {
    return 'gitpod';
  }
  
  if (window.location.hostname.includes('codespaces')) {
    return 'codespaces';
  }
  
  if (window.location.hostname.includes('run.app')) {
    return 'gcp-staging';
  }
  
  return 'development';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 15000, // Increased timeout for production
  headers: {
    'Content-Type': 'application/json',
  },
};

// Environment-specific settings
export const ENV_CONFIG = {
  environment: getEnvironment(),
  isDevelopment: getEnvironment() === 'development',
  isProduction: getEnvironment() === 'production',
  apiUrl: API_BASE_URL,
  debug: getEnvironment() === 'development',
};

// API endpoints configuration
export const API_ENDPOINTS = {
  // Dashboard endpoints
  dashboard: {
    stats: '/api/dashboard/stats',
    overview: '/api/dashboard/overview',
  },
  
  // Startups endpoints
  startups: {
    base: '/api/startups/',
    detail: (id) => `/api/startups/${id}`,
    search: '/api/startups/search/suggestions',
    status: (status) => `/api/startups/status/${status}/count`,
  },
  
  // Pipeline endpoints
  pipeline: {
    stats: '/api/pipeline/stats',
    stages: '/api/pipeline/stages',
    bottlenecks: '/api/pipeline/bottlenecks',
    throughput: '/api/pipeline/throughput',
    updateStatus: (id) => `/api/pipeline/applications/${id}/status`,
  },
  
  // Memos endpoints
  memos: {
    base: '/api/memos/',
    byStartup: (id) => `/api/memos/startup/${id}`,
    detail: (id) => `/api/memos/${id}`,
    approve: (id) => `/api/memos/${id}/approve`,
    scheduleReview: (id) => `/api/memos/${id}/schedule-review`,
    stats: '/api/memos/stats/summary',
  },
  
  // Uploads endpoints
  uploads: {
    files: '/api/uploads/files',
    startupFiles: (id) => `/api/uploads/startup/${id}/files`,
    fileDetail: (id) => `/api/uploads/files/${id}`,
    stats: '/api/uploads/stats/summary',
  },
  
  // Settings endpoints
  settings: {
    users: {
      me: '/api/settings/users/me',
      all: '/api/settings/users',
      invite: '/api/settings/users/invite',
      detail: (id) => `/api/settings/users/${id}`,
      role: (id) => `/api/settings/users/${id}/role`,
    },
    investmentWeights: '/api/settings/investment-weights',
    preferences: '/api/settings/account/preferences',
    systemInfo: '/api/settings/system/info',
    industries: '/api/settings/industries',
  },
  
  // Utility endpoints
  health: '/health',
  status: '/api/status',
};

// Logging utility for debugging API configuration
export const logApiConfig = () => {
  if (ENV_CONFIG.debug) {
    console.log('🔧 API Configuration:', {
      environment: ENV_CONFIG.environment,
      apiBaseUrl: API_BASE_URL,
      currentUrl: window.location.href,
      config: API_CONFIG,
    });
  }
};

// Initialize logging on module load
logApiConfig();