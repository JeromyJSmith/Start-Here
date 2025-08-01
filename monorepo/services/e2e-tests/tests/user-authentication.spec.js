/**
 * E2E tests for user authentication workflows
 * Following complete user journey testing approach
 */

import { test, expect } from '@playwright/test';

// Test data
const testUser = JSON.parse(process.env.E2E_TEST_USER || '{}');

test.describe('User Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Start each test from the home page
    await page.goto('/');
  });

  test('should display login form when not authenticated', async ({ page }) => {
    // Should show login form
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    // Fill login form
    await page.fill('input[name="username"]', testUser.username || 'testuser');
    await page.fill('input[name="password"]', testUser.password || 'testpass');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Should show user info
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    await expect(page.locator('text=' + (testUser.username || 'testuser'))).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill login form with wrong credentials
    await page.fill('input[name="username"]', 'wronguser');
    await page.fill('input[name="password"]', 'wrongpass');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('text=/Invalid credentials/i')).toBeVisible();
    
    // Should stay on login page
    await expect(page.locator('input[name="username"]')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // First login
    await page.fill('input[name="username"]', testUser.username || 'testuser');
    await page.fill('input[name="password"]', testUser.password || 'testpass');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Click user menu
    await page.click('[data-testid="user-menu"]');
    
    // Click logout
    await page.click('[data-testid="logout-button"]');
    
    // Should redirect to login page
    await expect(page).toHaveURL('/');
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('should handle session persistence', async ({ page, context }) => {
    // Login
    await page.fill('input[name="username"]', testUser.username || 'testuser');
    await page.fill('input[name="password"]', testUser.password || 'testpass');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Open new page in same context
    const newPage = await context.newPage();
    await newPage.goto('/');
    
    // Should be automatically logged in
    await expect(newPage).toHaveURL(/.*dashboard/);
    await expect(newPage.locator('[data-testid="user-menu"]')).toBeVisible();
    
    await newPage.close();
  });

  test('should handle session expiration', async ({ page }) => {
    // Login
    await page.fill('input[name="username"]', testUser.username || 'testuser');
    await page.fill('input[name="password"]', testUser.password || 'testpass');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Simulate session expiration by clearing storage
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Navigate to protected route
    await page.goto('/dashboard');
    
    // Should redirect to login
    await expect(page).toHaveURL('/');
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('should validate form inputs', async ({ page }) => {
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Should show validation errors
    await expect(page.locator('text=/Username is required/i')).toBeVisible();
    await expect(page.locator('text=/Password is required/i')).toBeVisible();
    
    // Fill only username
    await page.fill('input[name="username"]', 'testuser');
    await page.click('button[type="submit"]');
    
    // Should show password validation error
    await expect(page.locator('text=/Password is required/i')).toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    // Tab through form elements
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="username"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="password"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('button[type="submit"]')).toBeFocused();
    
    // Submit with Enter
    await page.fill('input[name="username"]', testUser.username || 'testuser');
    await page.fill('input[name="password"]', testUser.password || 'testpass');
    await page.locator('button[type="submit"]').focus();
    await page.keyboard.press('Enter');
    
    // Should login successfully
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('should handle loading states', async ({ page }) => {
    // Slow down network to see loading state
    await page.route('**/api/auth/login', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.continue();
    });
    
    // Fill and submit form
    await page.fill('input[name="username"]', testUser.username || 'testuser');
    await page.fill('input[name="password"]', testUser.password || 'testpass');
    await page.click('button[type="submit"]');
    
    // Should show loading indicator
    await expect(page.locator('[data-testid="login-loading"]')).toBeVisible();
    
    // Button should be disabled during loading
    await expect(page.locator('button[type="submit"]')).toBeDisabled();
    
    // Eventually should complete
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 10000 });
  });

  test('should be accessible', async ({ page }) => {
    // Check for accessibility attributes
    const usernameInput = page.locator('input[name="username"]');
    const passwordInput = page.locator('input[name="password"]');
    const submitButton = page.locator('button[type="submit"]');
    
    // Inputs should have labels
    await expect(usernameInput).toHaveAttribute('aria-label');
    await expect(passwordInput).toHaveAttribute('aria-label');
    
    // Button should have accessible name
    await expect(submitButton).toHaveAccessibleName();
    
    // Form should have proper structure
    await expect(page.locator('form')).toBeVisible();
    
    // Error messages should be associated with inputs
    await page.click('button[type="submit"]');
    const errorMessage = page.locator('[data-testid="error-message"]').first();
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toHaveAttribute('role', 'alert');
    }
  });
});