const { test, expect } = require('@playwright/test');

test.describe('Application Navigation', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load homepage without errors', async ({ page }) => {
    // Check for console errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Wait for page to load completely
    await page.waitForLoadState('networkidle');
    
    // Check for critical console errors (ignore common dev warnings)
    const criticalErrors = consoleErrors.filter(error => 
      !error.includes('Warning') && 
      !error.includes('webpack') &&
      !error.includes('DevTools')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('should have accessible navigation elements', async ({ page }) => {
    // Look for common navigation patterns
    const navElements = await page.locator('nav, .navbar, .navigation, [role="navigation"]').count();
    
    if (navElements > 0) {
      // Check if navigation is accessible
      const nav = page.locator('nav, .navbar, .navigation, [role="navigation"]').first();
      await expect(nav).toBeVisible();
      
      // Check for navigation links
      const navLinks = nav.locator('a, button');
      const linkCount = await navLinks.count();
      
      if (linkCount > 0) {
        // Test first few navigation links
        for (let i = 0; i < Math.min(3, linkCount); i++) {
          const link = navLinks.nth(i);
          await expect(link).toBeVisible();
        }
      }
    }
  });

  test('should handle navigation between pages', async ({ page }) => {
    // Look for internal navigation links
    const internalLinks = page.locator('a[href^="/"], a[href^="./"], a[href^="../"]');
    const linkCount = await internalLinks.count();
    
    if (linkCount > 0) {
      // Test navigation to first internal link
      const firstLink = internalLinks.first();
      const href = await firstLink.getAttribute('href');
      
      if (href && !href.includes('#')) {
        await firstLink.click();
        
        // Wait for navigation to complete
        await page.waitForLoadState('networkidle');
        
        // Verify URL changed or content updated
        const currentUrl = page.url();
        expect(currentUrl).toContain(href.replace('./', '').replace('../', ''));
      }
    }
  });

  test('should handle 404 pages gracefully', async ({ page }) => {
    // Navigate to non-existent page
    await page.goto('/non-existent-page');
    
    // Should not crash and either show 404 page or redirect
    await page.waitForLoadState('networkidle');
    
    // Check if there's a proper error page or redirect happened
    const bodyText = await page.textContent('body');
    const has404Content = bodyText.includes('404') || 
                          bodyText.includes('Not Found') || 
                          bodyText.includes('Page not found');
    
    const redirectedToHome = page.url().endsWith('/') || page.url().includes('/login');
    
    expect(has404Content || redirectedToHome).toBeTruthy();
  });
});

test.describe('Core Functionality', () => {
  
  test('should load main application components', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Look for React app root
    const reactRoot = page.locator('#root, #app, [data-reactroot]');
    await expect(reactRoot).toBeVisible();
    
    // Check if main content is present
    const mainContent = page.locator('main, [role="main"], .App, .container');
    if (await mainContent.count() > 0) {
      await expect(mainContent.first()).toBeVisible();
    }
  });

  test('should have proper page title', async ({ page }) => {
    await page.goto('/');
    
    const title = await page.title();
    expect(title).not.toBe('');
    expect(title).not.toBe('React App'); // Should be customized
  });

  test('should load without JavaScript errors', async ({ page }) => {
    const jsErrors = [];
    
    page.on('pageerror', error => {
      jsErrors.push(error.message);
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Filter out common development warnings
    const criticalErrors = jsErrors.filter(error => 
      !error.includes('Warning') && 
      !error.includes('DevTools') &&
      !error.toLowerCase().includes('warning')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('should handle form interactions', async ({ page }) => {
    await page.goto('/');
    
    // Look for any forms on the page
    const forms = page.locator('form');
    const formCount = await forms.count();
    
    if (formCount > 0) {
      const form = forms.first();
      
      // Find inputs in the form
      const inputs = form.locator('input, textarea, select');
      const inputCount = await inputs.count();
      
      if (inputCount > 0) {
        // Test first input interaction
        const firstInput = inputs.first();
        const inputType = await firstInput.getAttribute('type');
        
        if (inputType === 'text' || inputType === 'email' || !inputType) {
          await firstInput.fill('test input');
          await expect(firstInput).toHaveValue('test input');
        }
      }
    }
  });
});

test.describe('Performance and Accessibility', () => {
  
  test('should load within reasonable time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Should load within 10 seconds (generous for development)
    expect(loadTime).toBeLessThan(10000);
  });

  test('should have basic accessibility features', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check for basic accessibility features
    const hasHeadings = await page.locator('h1, h2, h3, h4, h5, h6').count() > 0;
    const hasAltTexts = await page.locator('img[alt]').count();
    const hasLabels = await page.locator('label, input[aria-label], input[placeholder]').count() > 0;
    
    // At least some accessibility features should be present
    expect(hasHeadings || hasLabels).toBeTruthy();
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');
    
    // Try tabbing through interactive elements
    await page.keyboard.press('Tab');
    
    // Check if focus is visible somewhere
    const focusedElement = page.locator(':focus');
    
    // If there are focusable elements, at least one should be focusable
    const focusableElements = page.locator('button, input, select, textarea, a[href]');
    const focusableCount = await focusableElements.count();
    
    if (focusableCount > 0) {
      // Should be able to focus on elements
      await focusableElements.first().focus();
      await expect(focusableElements.first()).toBeFocused();
    }
  });
});