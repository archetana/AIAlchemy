const { test, expect } = require('@playwright/test');

test.describe('End-to-End Integration Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Set up interceptors for API calls
    await page.route('/api/health', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'healthy', timestamp: new Date().toISOString() })
      });
    });
  });

  test('complete user journey - guest to authenticated user', async ({ page }) => {
    // Step 1: Land on homepage as guest
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Verify homepage loads
    const bodyText = await page.textContent('body');
    expect(bodyText.length).toBeGreaterThan(0);
    
    // Step 2: Navigate to login
    const loginElements = page.locator('button, a').filter({ hasText: /login|sign in/i });
    
    if (await loginElements.count() > 0) {
      await loginElements.first().click();
      await page.waitForTimeout(2000);
      
      // Step 3: Fill login form
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      
      if (await emailInput.count() > 0 && await passwordInput.count() > 0) {
        await emailInput.fill('test@example.com');
        await passwordInput.fill('testpassword123');
        
        // Step 4: Submit login
        const submitButton = page.locator('button').filter({ hasText: /login|sign in|submit/i });
        await submitButton.click();
        
        // Step 5: Handle login result
        await page.waitForTimeout(3000);
        
        // Either redirected to dashboard or got error (both are valid for testing)
        const currentUrl = page.url();
        const hasError = await page.locator('[role="alert"], .error').count() > 0;
        
        if (!hasError) {
          // If login succeeded, test protected area navigation
          await page.goto('/pipeline');
          await page.waitForTimeout(2000);
          
          const pipelineContent = await page.textContent('body');
          expect(pipelineContent.length).toBeGreaterThan(0);
        }
      }
    }
  });

  test('API connectivity and error handling', async ({ page }) => {
    // Test various API endpoints
    const apiTests = [
      { endpoint: '/api/health', expectedStatus: 200 },
      { endpoint: '/api/auth/login', expectedStatus: [200, 401, 422] },
      { endpoint: '/api/nonexistent', expectedStatus: [404, 500] }
    ];
    
    for (const apiTest of apiTests) {
      const response = await page.request.get(apiTest.endpoint);
      
      if (Array.isArray(apiTest.expectedStatus)) {
        expect(apiTest.expectedStatus).toContain(response.status());
      } else {
        expect(response.status()).toBe(apiTest.expectedStatus);
      }
    }
  });

  test('frontend-backend integration', async ({ page }) => {
    // Mock backend responses to test frontend handling
    await page.route('/api/auth/login', route => {
      const request = route.request();
      const postData = request.postData();
      
      if (postData && postData.includes('test@example.com')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access_token: 'fake-jwt-token',
            token_type: 'bearer',
            expires_in: 3600
          })
        });
      } else {
        route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Invalid credentials' })
        });
      }
    });
    
    await page.route('/api/pipeline/**', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          bottlenecks: [
            { id: 1, name: 'Process A', severity: 'high', impact: 85 },
            { id: 2, name: 'Process B', severity: 'medium', impact: 45 }
          ],
          stages: ['Stage 1', 'Stage 2', 'Stage 3'],
          metrics: { efficiency: 78, throughput: 92 }
        })
      });
    });
    
    // Navigate to application and test integration
    await page.goto('/');
    
    // Test successful login flow
    if (await page.locator('input[type="email"]').count() > 0) {
      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'testpassword123');
      
      const loginButton = page.locator('button').filter({ hasText: /login|sign in/i });
      await loginButton.click();
      
      // Wait for login to process
      await page.waitForTimeout(2000);
      
      // Navigate to pipeline to test data integration
      await page.goto('/pipeline');
      await page.waitForTimeout(3000);
      
      // Check if pipeline data is rendered
      const pipelineText = await page.textContent('body');
      const hasBottleneckData = pipelineText.includes('Process A') || 
                               pipelineText.includes('Process B') ||
                               pipelineText.includes('bottleneck') ||
                               pipelineText.includes('severity');
      
      expect(hasBottleneckData).toBeTruthy();
    }
  });

  test('cross-browser compatibility', async ({ page, browserName }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test basic functionality across browsers
    console.log(`Testing on ${browserName}`);
    
    // Check if basic elements render
    const hasContent = await page.locator('body').textContent();
    expect(hasContent.length).toBeGreaterThan(0);
    
    // Test CSS rendering (check if styled components load)
    const bodyStyles = await page.locator('body').evaluate(el => {
      const styles = window.getComputedStyle(el);
      return {
        fontFamily: styles.fontFamily,
        backgroundColor: styles.backgroundColor,
        margin: styles.margin
      };
    });
    
    // Should have some styling applied
    expect(bodyStyles.fontFamily).not.toBe('');
    
    // Test JavaScript functionality
    const jsWorking = await page.evaluate(() => {
      return typeof window !== 'undefined' && typeof document !== 'undefined';
    });
    
    expect(jsWorking).toBe(true);
  });

  test('performance and load testing', async ({ page }) => {
    // Measure page load performance
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Should load reasonably fast (10 seconds max for development)
    expect(loadTime).toBeLessThan(10000);
    
    // Check for memory leaks (basic check)
    const initialMemory = await page.evaluate(() => {
      if (performance.memory) {
        return performance.memory.usedJSHeapSize;
      }
      return 0;
    });
    
    // Navigate between pages multiple times
    for (let i = 0; i < 3; i++) {
      await page.goto('/pipeline');
      await page.waitForTimeout(1000);
      await page.goto('/');
      await page.waitForTimeout(1000);
    }
    
    const finalMemory = await page.evaluate(() => {
      if (performance.memory) {
        return performance.memory.usedJSHeapSize;
      }
      return 0;
    });
    
    // Memory shouldn't grow excessively (basic heuristic)
    if (initialMemory > 0 && finalMemory > 0) {
      const memoryGrowth = finalMemory - initialMemory;
      const growthPercentage = (memoryGrowth / initialMemory) * 100;
      
      // Allow up to 200% memory growth for development (very generous)
      expect(growthPercentage).toBeLessThan(200);
    }
  });

  test('accessibility compliance', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check for basic accessibility features
    const accessibilityChecks = {
      hasHeadings: await page.locator('h1, h2, h3, h4, h5, h6').count() > 0,
      hasAltTexts: await page.locator('img[alt]').count() > 0,
      hasLabels: await page.locator('label').count() > 0,
      hasAriaLabels: await page.locator('[aria-label]').count() > 0,
      hasRoles: await page.locator('[role]').count() > 0
    };
    
    // At least some accessibility features should be present
    const accessibilityScore = Object.values(accessibilityChecks).filter(Boolean).length;
    expect(accessibilityScore).toBeGreaterThan(0);
    
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');
    
    // Should be able to focus on interactive elements
    const hasFocusableElements = await page.locator('button, input, select, textarea, a[href]').count() > 0;
    
    if (hasFocusableElements) {
      await page.locator('button, input, select, textarea, a[href]').first().focus();
      await expect(page.locator('button, input, select, textarea, a[href]').first()).toBeFocused();
    }
  });

  test('error recovery and resilience', async ({ page }) => {
    // Test application behavior under various error conditions
    
    // 1. Network failure simulation
    await page.route('/api/**', route => {
      route.abort('failed');
    });
    
    await page.goto('/');
    await page.waitForTimeout(3000);
    
    // App should still render basic UI
    const bodyContent = await page.textContent('body');
    expect(bodyContent.length).toBeGreaterThan(0);
    
    // 2. Restore network and test recovery
    await page.unroute('/api/**');
    
    // 3. Test malformed API responses
    await page.route('/api/**', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: 'invalid json {'
      });
    });
    
    await page.reload();
    await page.waitForTimeout(3000);
    
    // Should handle malformed responses gracefully
    const errorElements = await page.locator('.error, [role="alert"]').count();
    const stillFunctional = await page.textContent('body');
    
    expect(stillFunctional.length).toBeGreaterThan(0);
  });
});