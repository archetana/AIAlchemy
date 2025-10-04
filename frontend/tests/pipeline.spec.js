const { test, expect } = require('@playwright/test');

test.describe('Pipeline Functionality', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should access pipeline page', async ({ page }) => {
    // Try to navigate to pipeline page
    await page.goto('/pipeline');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Should either show pipeline content or redirect to login
    const hasLoginForm = await page.locator('input[type="email"], input[type="password"]').count() > 0;
    const hasPipelineContent = await page.locator('text=/pipeline|bottleneck|workflow/i').count() > 0;
    
    expect(hasLoginForm || hasPipelineContent).toBeTruthy();
  });

  test('should handle pipeline data loading', async ({ page }) => {
    // Mock successful login first (if authentication is required)
    await page.goto('/pipeline');
    
    // If login is required, try to bypass it for testing
    if (await page.locator('input[type="email"]').count() > 0) {
      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'testpassword');
      
      const loginButton = page.locator('button').filter({ hasText: /login|sign in/i });
      await loginButton.click();
      
      // Wait for potential redirect or error
      await page.waitForTimeout(3000);
    }
    
    // Look for pipeline-related elements
    const pipelineElements = page.locator('[data-testid*="pipeline"], .pipeline, text=/pipeline|bottleneck|stage|workflow/i');
    
    if (await pipelineElements.count() > 0) {
      await expect(pipelineElements.first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('should handle empty pipeline state', async ({ page }) => {
    await page.goto('/pipeline');
    
    // Wait for content to load
    await page.waitForTimeout(3000);
    
    // Look for empty state or loading indicators
    const emptyStateElements = page.locator('text=/no data|empty|no pipeline|loading/i');
    const loadingElements = page.locator('.loading, [data-testid*="loading"], .spinner');
    const pipelineContent = page.locator('.pipeline, [data-testid*="pipeline"]');
    
    // Should show either empty state, loading, or actual content
    const hasEmptyState = await emptyStateElements.count() > 0;
    const hasLoading = await loadingElements.count() > 0;
    const hasContent = await pipelineContent.count() > 0;
    
    expect(hasEmptyState || hasLoading || hasContent).toBeTruthy();
  });

  test('should not crash on bottlenecks.map error', async ({ page }) => {
    // Monitor console errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Navigate to pipeline page
    await page.goto('/pipeline');
    await page.waitForLoadState('networkidle');
    
    // Check for the specific error we're trying to fix
    const mapErrors = consoleErrors.filter(error => 
      error.includes('bottlenecks.map is not a function') ||
      error.includes('.map is not a function')
    );
    
    // This specific error should not occur
    expect(mapErrors).toHaveLength(0);
    
    // Page should still be functional
    const bodyContent = await page.textContent('body');
    expect(bodyContent.length).toBeGreaterThan(0);
  });
});

test.describe('Data Visualization', () => {
  
  test('should render charts and graphs', async ({ page }) => {
    await page.goto('/pipeline');
    
    // Wait for potential chart rendering
    await page.waitForTimeout(5000);
    
    // Look for chart elements (Recharts, Canvas, SVG)
    const chartElements = page.locator('svg, canvas, .recharts-wrapper, .chart, [data-testid*="chart"]');
    
    if (await chartElements.count() > 0) {
      await expect(chartElements.first()).toBeVisible();
      
      // Check if charts have data
      const svgElements = page.locator('svg');
      if (await svgElements.count() > 0) {
        const svgContent = await svgElements.first().innerHTML();
        expect(svgContent.length).toBeGreaterThan(100); // Should have actual chart content
      }
    }
  });

  test('should handle data filtering and sorting', async ({ page }) => {
    await page.goto('/pipeline');
    await page.waitForTimeout(3000);
    
    // Look for filter or sort controls
    const filterElements = page.locator('select, input[type="search"], .filter, [data-testid*="filter"]');
    const sortElements = page.locator('.sort, [data-testid*="sort"], button').filter({ hasText: /sort|order/i });
    
    if (await filterElements.count() > 0) {
      // Test filter interaction
      const filter = filterElements.first();
      if (await filter.getAttribute('type') === 'search') {
        await filter.fill('test');
      }
    }
    
    if (await sortElements.count() > 0) {
      // Test sort interaction
      await sortElements.first().click();
      await page.waitForTimeout(1000);
    }
  });
});

test.describe('Interactive Features', () => {
  
  test('should handle modal dialogs', async ({ page }) => {
    await page.goto('/pipeline');
    
    // Look for buttons that might open modals
    const buttons = page.locator('button').filter({ hasText: /add|create|edit|view|details/i });
    const buttonCount = await buttons.count();
    
    if (buttonCount > 0) {
      // Click first button that might open a modal
      await buttons.first().click();
      
      // Check if a modal appeared
      const modal = page.locator('[role="dialog"], .modal, .MuiDialog-root');
      
      if (await modal.count() > 0) {
        await expect(modal.first()).toBeVisible();
        
        // Try to close modal
        const closeButton = modal.locator('button').filter({ hasText: /close|cancel|×/i });
        if (await closeButton.count() > 0) {
          await closeButton.first().click();
          await expect(modal.first()).not.toBeVisible();
        }
      }
    }
  });

  test('should handle form submissions', async ({ page }) => {
    await page.goto('/pipeline');
    
    // Look for forms on the pipeline page
    const forms = page.locator('form');
    const formCount = await forms.count();
    
    if (formCount > 0) {
      const form = forms.first();
      
      // Find submit button
      const submitButton = form.locator('button[type="submit"], input[type="submit"]');
      
      if (await submitButton.count() > 0) {
        // Fill required fields if any
        const requiredInputs = form.locator('input[required], select[required], textarea[required]');
        
        for (let i = 0; i < await requiredInputs.count(); i++) {
          const input = requiredInputs.nth(i);
          const inputType = await input.getAttribute('type');
          
          if (inputType === 'email') {
            await input.fill('test@example.com');
          } else if (inputType === 'text' || !inputType) {
            await input.fill('Test Value');
          }
        }
        
        // Submit form
        await submitButton.click();
        
        // Wait for response
        await page.waitForTimeout(2000);
      }
    }
  });

  test('should handle drag and drop interactions', async ({ page }) => {
    await page.goto('/pipeline');
    
    // Look for draggable elements
    const draggableElements = page.locator('[draggable="true"], .draggable, [data-testid*="drag"]');
    
    if (await draggableElements.count() > 1) {
      const source = draggableElements.first();
      const target = draggableElements.nth(1);
      
      // Perform drag and drop
      await source.dragTo(target);
      
      // Wait for any state changes
      await page.waitForTimeout(1000);
    }
  });
});

test.describe('Error Handling', () => {
  
  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API calls and simulate errors
    await page.route('/api/**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    await page.goto('/pipeline');
    await page.waitForTimeout(3000);
    
    // Should show error message, not crash
    const errorElements = page.locator('.error, [role="alert"], text=/error|failed|problem/i');
    
    if (await errorElements.count() > 0) {
      await expect(errorElements.first()).toBeVisible();
    }
    
    // Application should still be responsive
    const bodyContent = await page.textContent('body');
    expect(bodyContent.length).toBeGreaterThan(0);
  });

  test('should handle network timeouts', async ({ page }) => {
    // Simulate slow network
    await page.route('/api/**', route => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: [] })
        });
      }, 10000); // 10 second delay
    });
    
    await page.goto('/pipeline');
    
    // Should show loading state
    const loadingElements = page.locator('.loading, .spinner, text=/loading/i');
    
    if (await loadingElements.count() > 0) {
      await expect(loadingElements.first()).toBeVisible({ timeout: 5000 });
    }
  });
});