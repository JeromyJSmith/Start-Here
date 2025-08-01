/**
 * Global setup for E2E tests
 * Prepares test environment and data
 */

import { chromium } from '@playwright/test';

async function globalSetup() {
  console.log('🚀 Starting E2E test environment setup...');
  
  // Set up test environment variables
  process.env.NODE_ENV = 'test';
  process.env.TEST_DATABASE_URL = 'sqlite::memory:';
  
  // Create a browser instance for setup tasks
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Wait for services to be ready
    console.log('⏳ Waiting for services to be ready...');
    
    // Check frontend is ready
    await page.goto('http://localhost:3000', { 
      waitUntil: 'networkidle',
      timeout: 60000 
    });
    console.log('✅ Frontend service is ready');
    
    // Check backend is ready
    const response = await page.request.get('http://localhost:3001/health');
    if (response.ok()) {
      console.log('✅ Backend service is ready');
    } else {
      console.log('⚠️  Backend health check failed, continuing anyway');
    }
    
    // Set up test data
    await setupTestData(page);
    
    console.log('✅ E2E test environment setup completed');
    
  } catch (error) {
    console.error('❌ E2E test environment setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

async function setupTestData(page) {
  console.log('📋 Setting up test data...');
  
  try {
    // Create test user if needed
    const testUser = {
      username: 'e2e-test-user',
      email: 'e2e-test@example.com',
      password: 'e2e-test-password'
    };
    
    // Attempt to create test user via API
    try {
      await page.request.post('http://localhost:3001/api/auth/register', {
        data: testUser
      });
      console.log('✅ Test user created');
    } catch (error) {
      console.log('ℹ️  Test user may already exist or registration failed');
    }
    
    // Create test project
    const testProject = {
      name: 'E2E Test Project',
      path: '/tmp/e2e-test-project',
      description: 'Project for E2E testing'
    };
    
    // Save test data to global state
    process.env.E2E_TEST_USER = JSON.stringify(testUser);
    process.env.E2E_TEST_PROJECT = JSON.stringify(testProject);
    
    console.log('✅ Test data setup completed');
    
  } catch (error) {
    console.error('⚠️  Test data setup failed:', error);
    // Don't fail the entire setup for test data issues
  }
}

export default globalSetup;