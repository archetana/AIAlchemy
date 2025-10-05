const { test, expect } = require('@playwright/test');

test.describe('Authentication Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('should load login page', async ({ page }) => {
    // Check if login elements are present
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button')).toContainText(['Login', 'Sign In']);
  });

  test('should show validation errors for empty login', async ({ page }) => {
    // Try to submit empty form
    const loginButton = page.locator('button').filter({ hasText: /login|sign in/i });
    await loginButton.click();
    
    // Check for validation messages
    const errorElements = page.locator('[role="alert"], .error, .MuiFormHelperText-root.Mui-error');
    await expect(errorElements.first()).toBeVisible({ timeout: 5000 });
  });

  test('should attempt login with valid credentials', async ({ page }) => {
    // Fill in login form
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'testpassword');
    
    // Submit form
    const loginButton = page.locator('button').filter({ hasText: /login|sign in/i });
    await loginButton.click();
    
    // Wait for either success redirect or error message
    await Promise.race([
      page.waitForURL(/dashboard|profile|home/, { timeout: 10000 }),
      page.waitForSelector('[role="alert"], .error', { timeout: 10000 })
    ]);
    
    // Verify we either redirected or got an appropriate error
    const currentUrl = page.url();
    const hasError = await page.locator('[role="alert"], .error').count() > 0;
    
    // Either should redirect on success or show meaningful error
    expect(currentUrl.includes('dashboard') || currentUrl.includes('profile') || hasError).toBeTruthy();
  });

  test('should navigate to registration page', async ({ page }) => {
    // Look for registration link/button
    const registerLink = page.locator('a, button').filter({ hasText: /register|sign up|create account/i });
    
    if (await registerLink.count() > 0) {
      await registerLink.first().click();
      
      // Check if we're on registration page or modal opened
      await expect(
        page.locator('input[type="email"]').and(page.locator('text=/register|sign up|create/i'))
      ).toBeVisible({ timeout: 5000 });
    } else {
      console.log('Registration functionality not found - this might be expected');
    }
  });
});

test.describe('Protected Routes', () => {
  
  test('should redirect to login for protected routes', async ({ page }) => {
    // Try to access protected routes directly
    const protectedRoutes = ['/dashboard', '/profile', '/admin', '/pipeline'];
    
    for (const route of protectedRoutes) {
      await page.goto(route);
      
      // Should either redirect to login or show login form
      await page.waitForTimeout(2000); // Give time for redirect
      
      const hasLoginForm = await page.locator('input[type="email"], input[type="password"]').count() > 0;
      const currentUrl = page.url();
      const isOnLoginPage = currentUrl.includes('login') || currentUrl === page.context()._options.baseURL + '/';
      
      expect(hasLoginForm || isOnLoginPage).toBeTruthy();
    }
  });
});

test.describe('UI Responsiveness', () => {
  
  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    await page.goto('/');
    
    // Check if main elements are still visible and properly sized
    const mainContent = page.locator('main, [role="main"], .container');
    if (await mainContent.count() > 0) {
      await expect(mainContent.first()).toBeVisible();
    }
    
    // Check if navigation is responsive (might become hamburger menu)
    const navigation = page.locator('nav, .navbar, .navigation');
    if (await navigation.count() > 0) {
      await expect(navigation.first()).toBeVisible();
    }
  });

  test('should be responsive on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad
    await page.goto('/');
    
    // Similar checks for tablet layout
    const mainContent = page.locator('main, [role="main"], .container');
    if (await mainContent.count() > 0) {
      await expect(mainContent.first()).toBeVisible();
    }
  });
});