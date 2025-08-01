/**
 * E2E tests for complete Claude Code workflow
 * Tests the core user journey from project creation to code interaction
 */

import { test, expect } from '@playwright/test';

const testUser = JSON.parse(process.env.E2E_TEST_USER || '{}');
const testProject = JSON.parse(process.env.E2E_TEST_PROJECT || '{}');

test.describe('Claude Code Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.fill('input[name="username"]', testUser.username || 'testuser');
    await page.fill('input[name="password"]', testUser.password || 'testpass');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('should create a new project', async ({ page }) => {
    // Navigate to projects
    await page.click('[data-testid="projects-nav"]');
    
    // Click create project button
    await page.click('[data-testid="create-project-button"]');
    
    // Fill project form
    await page.fill('input[name="projectName"]', testProject.name || 'Test Project');
    await page.fill('input[name="projectPath"]', testProject.path || '/tmp/test-project');
    await page.fill('textarea[name="description"]', testProject.description || 'Test project description');
    
    // Submit form
    await page.click('button[data-testid="create-project-submit"]');
    
    // Should show success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // Should display project in list
    await expect(page.locator(`text=${testProject.name || 'Test Project'}`)).toBeVisible();
  });

  test('should open project and start coding session', async ({ page }) => {
    // Navigate to projects
    await page.click('[data-testid="projects-nav"]');
    
    // Open existing project
    await page.click(`[data-testid="project-${testProject.name?.replace(/\s+/g, '-').toLowerCase() || 'test-project'}"]`);
    
    // Should open code interface
    await expect(page.locator('[data-testid="code-interface"]')).toBeVisible();
    
    // Should show file tree
    await expect(page.locator('[data-testid="file-tree"]')).toBeVisible();
    
    // Should show chat interface
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
  });

  test('should send message to Claude and receive response', async ({ page }) => {
    // Open project
    await page.click('[data-testid="projects-nav"]');
    await page.click(`[data-testid="project-${testProject.name?.replace(/\s+/g, '-').toLowerCase() || 'test-project'}"]`);
    
    // Wait for interface to load
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    
    // Type message in chat
    const chatInput = page.locator('[data-testid="chat-input"]');
    await chatInput.fill('Hello, can you help me create a simple Python function?');
    
    // Send message
    await page.click('[data-testid="send-message-button"]');
    
    // Should show message in chat
    await expect(page.locator('[data-testid="user-message"]').last()).toContainText('Hello, can you help me create a simple Python function?');
    
    // Should show loading indicator
    await expect(page.locator('[data-testid="message-loading"]')).toBeVisible();
    
    // Should receive response (with timeout for API call)
    await expect(page.locator('[data-testid="claude-message"]').last()).toBeVisible({ timeout: 30000 });
    
    // Response should contain code or helpful content
    const response = page.locator('[data-testid="claude-message"]').last();
    await expect(response).toContainText(/def |function|python/i);
  });

  test('should handle file operations', async ({ page }) => {
    // Open project
    await page.click('[data-testid="projects-nav"]');
    await page.click(`[data-testid="project-${testProject.name?.replace(/\s+/g, '-').toLowerCase() || 'test-project'}"]`);
    
    await expect(page.locator('[data-testid="file-tree"]')).toBeVisible();
    
    // Right-click in file tree to create new file
    await page.click('[data-testid="file-tree"]', { button: 'right' });
    
    // Should show context menu
    await expect(page.locator('[data-testid="context-menu"]')).toBeVisible();
    
    // Click new file option
    await page.click('[data-testid="new-file-option"]');
    
    // Enter filename
    await page.fill('[data-testid="filename-input"]', 'test.py');
    await page.keyboard.press('Enter');
    
    // Should create file and open in editor
    await expect(page.locator('[data-testid="code-editor"]')).toBeVisible();
    await expect(page.locator('text=test.py')).toBeVisible();
  });

  test('should handle code editing and saving', async ({ page }) => {
    // Open project and create file
    await page.click('[data-testid="projects-nav"]');
    await page.click(`[data-testid="project-${testProject.name?.replace(/\s+/g, '-').toLowerCase() || 'test-project'}"]`);
    
    // Create or open a file
    await expect(page.locator('[data-testid="file-tree"]')).toBeVisible();
    
    // If file doesn't exist, create it
    await page.click('[data-testid="file-tree"]', { button: 'right' });
    if (await page.locator('[data-testid="new-file-option"]').isVisible()) {
      await page.click('[data-testid="new-file-option"]');
      await page.fill('[data-testid="filename-input"]', 'main.py');
      await page.keyboard.press('Enter');
    }
    
    // Wait for editor
    await expect(page.locator('[data-testid="code-editor"]')).toBeVisible();
    
    // Type some code
    const editor = page.locator('[data-testid="code-editor"]');
    await editor.click();
    await page.keyboard.type('def hello_world():\n    print("Hello, World!")\n\nhello_world()');
    
    // Save file (Ctrl+S)
    await page.keyboard.press('ControlOrMeta+s');
    
    // Should show save confirmation
    await expect(page.locator('[data-testid="save-indicator"]')).toBeVisible();
  });

  test('should handle terminal operations', async ({ page }) => {
    // Open project
    await page.click('[data-testid="projects-nav"]');
    await page.click(`[data-testid="project-${testProject.name?.replace(/\s+/g, '-').toLowerCase() || 'test-project'}"]`);
    
    // Open terminal
    await page.click('[data-testid="terminal-toggle"]');
    
    // Should show terminal
    await expect(page.locator('[data-testid="terminal"]')).toBeVisible();
    
    // Type command in terminal
    await page.locator('[data-testid="terminal"]').click();
    await page.keyboard.type('echo "Hello from terminal"');
    await page.keyboard.press('Enter');
    
    // Should show command output
    await expect(page.locator('[data-testid="terminal"]')).toContainText('Hello from terminal');
  });

  test('should handle dark mode toggle', async ({ page }) => {
    // Open project
    await page.click('[data-testid="projects-nav"]');
    await page.click(`[data-testid="project-${testProject.name?.replace(/\s+/g, '-').toLowerCase() || 'test-project'}"]`);
    
    // Find dark mode toggle
    const darkModeToggle = page.locator('[data-testid="dark-mode-toggle"]');
    await expect(darkModeToggle).toBeVisible();
    
    // Get initial theme state
    const initialIsDark = await page.locator('html').getAttribute('class');
    
    // Toggle dark mode
    await darkModeToggle.click();
    
    // Wait for theme change
    await page.waitForTimeout(500);
    
    // Check theme changed
    const newIsDark = await page.locator('html').getAttribute('class');
    expect(newIsDark).not.toBe(initialIsDark);
    
    // Toggle back
    await darkModeToggle.click();
    await page.waitForTimeout(500);
    
    // Should return to original theme
    const finalIsDark = await page.locator('html').getAttribute('class');
    expect(finalIsDark).toBe(initialIsDark);
  });

  test('should handle session management and recovery', async ({ page, context }) => {
    // Open project and start working
    await page.click('[data-testid="projects-nav"]');
    await page.click(`[data-testid="project-${testProject.name?.replace(/\s+/g, '-').toLowerCase() || 'test-project'}"]`);
    
    // Send a message to establish session
    await page.fill('[data-testid="chat-input"]', 'Start working on this project');
    await page.click('[data-testid="send-message-button"]');
    
    // Wait for response to establish session
    await expect(page.locator('[data-testid="claude-message"]').last()).toBeVisible({ timeout: 30000 });
    
    // Refresh page to simulate session recovery
    await page.reload();
    
    // Should maintain project state
    await expect(page.locator('[data-testid="code-interface"]')).toBeVisible();
    
    // Chat history should be preserved
    await expect(page.locator('[data-testid="user-message"]')).toBeVisible();
  });

  test('should handle error states gracefully', async ({ page }) => {
    // Mock network failure
    await page.route('**/api/chat/message', route => route.abort());
    
    // Open project
    await page.click('[data-testid="projects-nav"]');
    await page.click(`[data-testid="project-${testProject.name?.replace(/\s+/g, '-').toLowerCase() || 'test-project'}"]`);
    
    // Try to send message
    await page.fill('[data-testid="chat-input"]', 'This should fail');
    await page.click('[data-testid="send-message-button"]');
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('text=/connection error|network error|failed to send/i')).toBeVisible();
    
    // Should allow retry
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to project
    await page.click('[data-testid="mobile-menu-toggle"]');
    await page.click('[data-testid="projects-nav"]');
    await page.click(`[data-testid="project-${testProject.name?.replace(/\s+/g, '-').toLowerCase() || 'test-project'}"]`);
    
    // Should show mobile-optimized interface
    await expect(page.locator('[data-testid="mobile-code-interface"]')).toBeVisible();
    
    // Chat should be collapsible on mobile
    const chatToggle = page.locator('[data-testid="mobile-chat-toggle"]');
    if (await chatToggle.isVisible()) {
      await chatToggle.click();
      await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    }
  });
});