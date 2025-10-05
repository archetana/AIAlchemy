/**
 * Version Management for AIAlchemy
 * Auto-increments on each deployment
 */

// Version configuration
const VERSION_CONFIG = {
  major: 1,
  minor: 0,
  patch: 3,
  build: process.env.REACT_APP_BUILD_NUMBER || '59652338', // Use build number or timestamp
};

// Generate version string
export const getVersion = () => {
  return `${VERSION_CONFIG.major}.${VERSION_CONFIG.minor}.${VERSION_CONFIG.patch}.${VERSION_CONFIG.build}`;
};

// App metadata - static definition to avoid circular references
export const APP_INFO = {
  name: 'AIAlchemy',
  fullName: 'AIAlchemy - AI Analyst for Startup Evaluation',
  version: `${VERSION_CONFIG.major}.${VERSION_CONFIG.minor}.${VERSION_CONFIG.patch}.${VERSION_CONFIG.build}`, // Direct calculation
  description: 'AI-powered startup evaluation platform with automated due diligence, AI interviews, and investment memo generation',
  team: 'AIAlchemy Team',
  credits: [
    'Built with ❤️ by the AIAlchemy Team',
    'Powered by Google Cloud AI Services',
    'Document processing by Google Document AI',
    'Investment analysis by Google Gemini Pro'
  ],
  buildDate: '2025-10-05T08:18:58.450935',
  repository: 'https://github.com/archetana/AIAlchemy',
  license: 'MIT License',
  technologies: [
    'React 18+ with Material-UI',
    'FastAPI with Python 3.11+',
    'Google Cloud Vertex AI',
    'Document AI & Gemini Pro',
    'SQLite with SQLAlchemy',
    'Real-time processing pipeline'
  ]
};

// Deployment tracking - safer environment variable access
const getEnvVar = (name, defaultValue) => {
  try {
    return process.env[name] || defaultValue;
  } catch (error) {
    return defaultValue;
  }
};

export const DEPLOYMENT_INFO = {
  environment: getEnvVar('NODE_ENV', 'development'),
  buildNumber: getEnvVar('REACT_APP_BUILD_NUMBER', '59652338'),
  commitHash: getEnvVar('REACT_APP_COMMIT_HASH', 'local-dev'),
  buildDate: getEnvVar('REACT_APP_BUILD_DATE', '2025-10-05T08:18:58.450935'),
  deploymentDate: new Date().toISOString()
};

export default {
  VERSION_CONFIG,
  APP_INFO,
  DEPLOYMENT_INFO,
  getVersion
};