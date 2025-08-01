/**
 * Global teardown for E2E tests
 * Cleans up test environment and data
 */

import { chromium } from '@playwright/test';

async function globalTeardown() {
  console.log('🧹 Starting E2E test environment cleanup...');
  
  // Create a browser instance for cleanup tasks
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Clean up test data
    await cleanupTestData(page);
    
    console.log('✅ E2E test environment cleanup completed');
    
  } catch (error) {
    console.error('⚠️  E2E test environment cleanup failed:', error);
    // Don't fail teardown - just log the error
  } finally {
    await browser.close();
  }
}

async function cleanupTestData(page) {
  console.log('🗑️  Cleaning up test data...');
  
  try {
    // Get test user data from environment
    const testUserData = process.env.E2E_TEST_USER;
    if (testUserData) {
      const testUser = JSON.parse(testUserData);
      
      // Attempt to delete test user via API
      try {
        await page.request.delete(`http://localhost:3001/api/users/${testUser.username}`);
        console.log('✅ Test user cleaned up');
      } catch (error) {
        console.log('ℹ️  Test user cleanup failed or user doesn\'t exist');
      }
    }
    
    // Clean up test projects
    const testProjectData = process.env.E2E_TEST_PROJECT;
    if (testProjectData) {
      const testProject = JSON.parse(testProjectData);
      
      try {
        await page.request.delete(`http://localhost:3001/api/projects/by-path`, {
          data: { path: testProject.path }
        });
        console.log('✅ Test project cleaned up');
      } catch (error) {
        console.log('ℹ️  Test project cleanup failed or project doesn\'t exist');
      }
    }
    
    console.log('✅ Test data cleanup completed');
    
  } catch (error) {
    console.error('⚠️  Test data cleanup failed:', error);
  }
}

export default globalTeardown;