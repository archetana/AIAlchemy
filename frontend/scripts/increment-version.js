#!/usr/bin/env node

/**
 * Version Increment Script for AIAlchemy
 * Automatically increments patch version and updates build metadata
 */

const fs = require('fs');
const path = require('path');

const VERSION_FILE_PATH = path.join(__dirname, '../src/config/version.js');
const PACKAGE_JSON_PATH = path.join(__dirname, '../package.json');

// Read current version configuration
function readVersionConfig() {
  const content = fs.readFileSync(VERSION_FILE_PATH, 'utf8');
  
  // Extract current version numbers using regex
  const majorMatch = content.match(/major:\s*(\d+)/);
  const minorMatch = content.match(/minor:\s*(\d+)/);
  const patchMatch = content.match(/patch:\s*(\d+)/);
  
  return {
    major: majorMatch ? parseInt(majorMatch[1]) : 1,
    minor: minorMatch ? parseInt(minorMatch[1]) : 0,
    patch: patchMatch ? parseInt(patchMatch[1]) : 0
  };
}

// Update package.json version
function updatePackageJson(version) {
  const packageJson = JSON.parse(fs.readFileSync(PACKAGE_JSON_PATH, 'utf8'));
  packageJson.version = `${version.major}.${version.minor}.${version.patch}`;
  fs.writeFileSync(PACKAGE_JSON_PATH, JSON.stringify(packageJson, null, 2) + '\n');
  console.log(`✅ Updated package.json to version ${packageJson.version}`);
}

// Generate new version configuration
function generateVersionConfig(version, buildInfo) {
  const buildNumber = buildInfo.buildNumber || Date.now().toString().slice(-8);
  const commitHash = buildInfo.commitHash || 'unknown';
  const buildDate = new Date().toISOString();
  
  return `/**
 * Version Management for AIAlchemy
 * Auto-increments on each deployment
 */

// Version configuration
const VERSION_CONFIG = {
  major: ${version.major},
  minor: ${version.minor},
  patch: ${version.patch},
  build: process.env.REACT_APP_BUILD_NUMBER || '${buildNumber}', // Use build number or timestamp
};

// Generate version string
export const getVersion = () => {
  return \`\${VERSION_CONFIG.major}.\${VERSION_CONFIG.minor}.\${VERSION_CONFIG.patch}.\${VERSION_CONFIG.build}\`;
};

// App metadata
export const APP_INFO = {
  name: 'AIAlchemy',
  fullName: 'AIAlchemy - AI Analyst for Startup Evaluation',
  version: getVersion(),
  description: 'AI-powered startup evaluation platform with automated due diligence, AI interviews, and investment memo generation',
  team: 'AIAlchemy Team',
  credits: [
    'Built with ❤️ by the AIAlchemy Team',
    'Powered by Google Cloud AI Services',
    'Document processing by Google Document AI',
    'Investment analysis by Google Gemini Pro'
  ],
  buildDate: '${buildDate}',
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

// Deployment tracking
export const DEPLOYMENT_INFO = {
  environment: process.env.NODE_ENV || 'development',
  buildNumber: process.env.REACT_APP_BUILD_NUMBER || '${buildNumber}',
  commitHash: process.env.REACT_APP_COMMIT_HASH || '${commitHash}',
  buildDate: process.env.REACT_APP_BUILD_DATE || '${buildDate}',
  deploymentDate: new Date().toISOString()
};

export default {
  VERSION_CONFIG,
  APP_INFO,
  DEPLOYMENT_INFO,
  getVersion
};`;
}

// Main function
function incrementVersion(type = 'patch') {
  console.log('🚀 Incrementing version for AIAlchemy...\n');
  
  // Read current version
  const currentVersion = readVersionConfig();
  console.log(`📋 Current version: ${currentVersion.major}.${currentVersion.minor}.${currentVersion.patch}`);
  
  // Increment version based on type
  const newVersion = { ...currentVersion };
  
  switch (type.toLowerCase()) {
    case 'major':
      newVersion.major += 1;
      newVersion.minor = 0;
      newVersion.patch = 0;
      break;
    case 'minor':
      newVersion.minor += 1;
      newVersion.patch = 0;
      break;
    case 'patch':
    default:
      newVersion.patch += 1;
      break;
  }
  
  console.log(`🔢 New version: ${newVersion.major}.${newVersion.minor}.${newVersion.patch}`);
  
  // Get build information from environment or git
  const buildInfo = {
    buildNumber: process.env.BUILD_NUMBER || process.env.GITHUB_RUN_NUMBER,
    commitHash: process.env.COMMIT_SHA || process.env.GITHUB_SHA,
  };
  
  if (buildInfo.commitHash) {
    buildInfo.commitHash = buildInfo.commitHash.substring(0, 8); // Short hash
  }
  
  console.log(`🏗️  Build number: ${buildInfo.buildNumber || 'auto-generated'}`);
  console.log(`📝 Commit hash: ${buildInfo.commitHash || 'unknown'}`);
  
  // Generate and write new version configuration
  const newConfig = generateVersionConfig(newVersion, buildInfo);
  fs.writeFileSync(VERSION_FILE_PATH, newConfig);
  console.log(`✅ Updated version.js`);
  
  // Update package.json
  updatePackageJson(newVersion);
  
  console.log(`\n🎉 Version increment complete! New version: ${newVersion.major}.${newVersion.minor}.${newVersion.patch}`);
  
  return newVersion;
}

// Run if called directly
if (require.main === module) {
  const versionType = process.argv[2] || 'patch';
  incrementVersion(versionType);
}

module.exports = incrementVersion;