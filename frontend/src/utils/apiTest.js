/**
 * API Testing Utilities for Development and Production
 * Test API connectivity and environment detection
 */

import { apiUtils } from '../services/api.js';
import { ENV_CONFIG, API_CONFIG } from '../config/api.js';

export class ApiTestSuite {
  constructor() {
    this.results = {};
  }

  /**
   * Run comprehensive API tests
   */
  async runAllTests() {
    console.log('🧪 Starting API Test Suite...');
    console.log('================================');
    
    const tests = [
      this.testEnvironmentDetection,
      this.testApiConfiguration,
      this.testApiConnectivity,
      this.testHealthEndpoint,
      this.testApiStatus,
    ];

    for (const test of tests) {
      try {
        await test.call(this);
      } catch (error) {
        console.error(`❌ Test failed: ${test.name}`, error);
        this.results[test.name] = { success: false, error: error.message };
      }
    }

    this.printResults();
    return this.results;
  }

  /**
   * Test environment detection logic
   */
  async testEnvironmentDetection() {
    console.log('🌍 Testing Environment Detection...');
    
    const envInfo = {
      hostname: window.location.hostname,
      port: window.location.port,
      protocol: window.location.protocol,
      detectedEnv: ENV_CONFIG.environment,
      isProduction: ENV_CONFIG.isProduction,
      isDevelopment: ENV_CONFIG.isDevelopment,
      apiUrl: API_CONFIG.baseURL,
    };

    console.log('Environment Info:', envInfo);
    
    // Validate environment logic
    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1';
    
    const expectedEnv = isLocalhost ? 'development' : 
                       window.location.hostname.includes('gitpod') ? 'gitpod' :
                       window.location.hostname.includes('codespaces') ? 'codespaces' :
                       'production';

    const envCorrect = ENV_CONFIG.environment === expectedEnv;
    
    this.results.testEnvironmentDetection = {
      success: envCorrect,
      data: envInfo,
      expected: expectedEnv,
      actual: ENV_CONFIG.environment,
    };

    if (envCorrect) {
      console.log('✅ Environment detection: PASSED');
    } else {
      console.log(`❌ Environment detection: FAILED (expected: ${expectedEnv}, got: ${ENV_CONFIG.environment})`);
    }
  }

  /**
   * Test API configuration setup
   */
  async testApiConfiguration() {
    console.log('⚙️ Testing API Configuration...');
    
    const config = apiUtils.getApiConfig();
    console.log('API Configuration:', config);
    
    // Validate configuration
    const hasBaseURL = !!config.baseURL;
    const hasTimeout = config.timeout > 0;
    const validUrl = config.baseURL.startsWith('http');
    
    const configValid = hasBaseURL && hasTimeout && validUrl;
    
    this.results.testApiConfiguration = {
      success: configValid,
      data: config,
      checks: { hasBaseURL, hasTimeout, validUrl },
    };

    if (configValid) {
      console.log('✅ API configuration: PASSED');
    } else {
      console.log('❌ API configuration: FAILED');
    }
  }

  /**
   * Test basic API connectivity
   */
  async testApiConnectivity() {
    console.log('🔗 Testing API Connectivity...');
    
    try {
      const response = await apiUtils.testConnection();
      const isHealthy = response.status === 200 && response.data;
      
      this.results.testApiConnectivity = {
        success: isHealthy,
        data: response.data,
        status: response.status,
      };

      if (isHealthy) {
        console.log('✅ API connectivity: PASSED');
        console.log('Health response:', response.data);
      } else {
        console.log('❌ API connectivity: FAILED');
      }
    } catch (error) {
      console.log('❌ API connectivity: FAILED');
      console.error('Connection error:', error.message);
      
      this.results.testApiConnectivity = {
        success: false,
        error: error.message,
        code: error.code || 'UNKNOWN',
      };
    }
  }

  /**
   * Test health endpoint specifically
   */
  async testHealthEndpoint() {
    console.log('❤️ Testing Health Endpoint...');
    
    try {
      const response = await apiUtils.testConnection();
      const healthData = response.data;
      
      // Validate health response structure
      const hasStatus = healthData && healthData.status;
      const isHealthy = hasStatus && healthData.status === 'healthy';
      
      this.results.testHealthEndpoint = {
        success: isHealthy,
        data: healthData,
        hasStatus,
        status: healthData?.status,
      };

      if (isHealthy) {
        console.log('✅ Health endpoint: PASSED');
      } else {
        console.log('❌ Health endpoint: FAILED (unhealthy status)');
      }
    } catch (error) {
      console.log('❌ Health endpoint: FAILED');
      this.results.testHealthEndpoint = {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Test API status endpoint
   */
  async testApiStatus() {
    console.log('📊 Testing API Status...');
    
    try {
      const response = await apiUtils.getApiStatus();
      const statusData = response.data;
      
      // Validate status response
      const hasApi = statusData && statusData.api;
      const isOperational = hasApi && statusData.api === 'operational';
      
      this.results.testApiStatus = {
        success: isOperational,
        data: statusData,
        hasApi,
        apiStatus: statusData?.api,
      };

      if (isOperational) {
        console.log('✅ API status: PASSED');
        console.log('Available endpoints:', Object.keys(statusData.available_endpoints || {}));
      } else {
        console.log('❌ API status: FAILED');
      }
    } catch (error) {
      console.log('❌ API status: FAILED');
      this.results.testApiStatus = {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Print comprehensive test results
   */
  printResults() {
    console.log('');
    console.log('📋 Test Results Summary');
    console.log('========================');
    
    const testNames = Object.keys(this.results);
    const totalTests = testNames.length;
    const passedTests = testNames.filter(name => this.results[name].success).length;
    const failedTests = totalTests - passedTests;
    
    testNames.forEach(testName => {
      const result = this.results[testName];
      const status = result.success ? '✅ PASS' : '❌ FAIL';
      console.log(`${status} ${testName}`);
      
      if (!result.success && result.error) {
        console.log(`   Error: ${result.error}`);
      }
    });
    
    console.log('');
    console.log(`📊 Results: ${passedTests}/${totalTests} tests passed`);
    
    if (failedTests > 0) {
      console.log(`⚠️ ${failedTests} test(s) failed - check configuration`);
    } else {
      console.log('🎉 All tests passed! API is ready for use.');
    }
    
    console.log('');
    console.log('🔧 Current Configuration:');
    console.log(`   Environment: ${ENV_CONFIG.environment}`);
    console.log(`   API URL: ${API_CONFIG.baseURL}`);
    console.log(`   Timeout: ${API_CONFIG.timeout}ms`);
  }
}

/**
 * Quick test function for console use
 */
export const quickApiTest = async () => {
  const testSuite = new ApiTestSuite();
  return await testSuite.runAllTests();
};

/**
 * Environment info for debugging
 */
export const getEnvironmentInfo = () => {
  return {
    url: window.location.href,
    hostname: window.location.hostname,
    port: window.location.port,
    protocol: window.location.protocol,
    environment: ENV_CONFIG.environment,
    apiBaseUrl: API_CONFIG.baseURL,
    timestamp: new Date().toISOString(),
  };
};

// Export for global access in development
if (ENV_CONFIG.isDevelopment) {
  window.apiTest = {
    runTests: quickApiTest,
    envInfo: getEnvironmentInfo,
    testSuite: ApiTestSuite,
  };
  
  console.log('🔧 API Test utilities available at window.apiTest');
  console.log('   Use window.apiTest.runTests() to run all tests');
  console.log('   Use window.apiTest.envInfo() to see environment info');
}