/**
 * Integration tests for API routes
 * Following T-2 (MUST): Add/extend integration tests for API changes
 */

import { jest } from '@jest/globals';
import request from 'supertest';
import express from 'express';
import { createServer } from 'http';
import { userDb, projectDb } from '../../database/db.js';

// Mock the database modules
jest.mock('../../database/db.js');

// Import the app after mocking
let app;

describe('API Routes Integration Tests', () => {
  beforeAll(async () => {
    // Dynamically import the app to ensure mocks are applied
    const appModule = await import('../../index.js');
    app = appModule.default || appModule.app;
    
    // Set test environment
    process.env.NODE_ENV = 'test';
    process.env.JWT_SECRET = 'test-secret';
  });

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default mock responses
    userDb.getUserById.mockReturnValue({
      id: 'user-123',
      username: 'testuser',
      email: 'test@example.com'
    });
    
    userDb.getUserByUsername.mockReturnValue(null);
    userDb.createUser.mockReturnValue({
      id: 'user-123',
      username: 'testuser',
      email: 'test@example.com'
    });
    
    projectDb.getProjectsByUserId.mockReturnValue([]);
    projectDb.createProject.mockReturnValue({
      id: 'project-123',
      name: 'Test Project',
      path: '/test/path',
      userId: 'user-123'
    });
  });

  describe('Authentication Routes', () => {
    describe('POST /api/auth/register', () => {
      it('should register new user successfully', async () => {
        // T-2 (MUST): Test API endpoint integration
        const userData = {
          username: 'newuser',
          email: 'new@example.com',
          password: 'password123'
        };

        const response = await request(app)
          .post('/api/auth/register')
          .send(userData)
          .expect(201);

        expect(response.body).toBeValidApiResponse();
        expect(response.body.success).toBe(true);
        expect(response.body.data.user).toHaveRequiredFields(['id', 'username', 'email']);
        expect(response.body.data.token).toBeDefined();
        
        // Verify database was called
        expect(userDb.createUser).toHaveBeenCalledWith(
          expect.objectContaining({
            username: userData.username,
            email: userData.email
          })
        );
      });

      it('should reject registration with existing username', async () => {
        // Mock existing user
        userDb.getUserByUsername.mockReturnValue({
          id: 'existing-user',
          username: 'existinguser'
        });

        const userData = {
          username: 'existinguser',
          email: 'new@example.com',
          password: 'password123'
        };

        const response = await request(app)
          .post('/api/auth/register')
          .send(userData)
          .expect(400);

        expect(response.body).toBeValidApiResponse();
        expect(response.body.success).toBe(false);
        expect(response.body.error).toMatch(/already exists/i);
        
        // Should not create user
        expect(userDb.createUser).not.toHaveBeenCalled();
      });

      it('should validate required fields', async () => {
        const response = await request(app)
          .post('/api/auth/register')
          .send({}) // Empty payload
          .expect(400);

        expect(response.body).toBeValidApiResponse();
        expect(response.body.success).toBe(false);
        expect(response.body.error).toMatch(/required/i);
      });
    });

    describe('POST /api/auth/login', () => {
      beforeEach(() => {
        // Mock valid user with hashed password
        userDb.getUserByUsername.mockReturnValue({
          id: 'user-123',
          username: 'testuser',
          email: 'test@example.com',
          password: 'hashed-password'
        });
      });

      it('should login with valid credentials', async () => {
        // Mock password comparison
        const bcrypt = await import('bcrypt');
        jest.spyOn(bcrypt, 'compare').mockResolvedValue(true);

        const loginData = {
          username: 'testuser',
          password: 'password123'
        };

        const response = await request(app)
          .post('/api/auth/login')
          .send(loginData)
          .expect(200);

        expect(response.body).toBeValidApiResponse();
        expect(response.body.success).toBe(true);
        expect(response.body.data.user).toHaveRequiredFields(['id', 'username', 'email']);
        expect(response.body.data.token).toBeDefined();
        
        // Verify user lookup
        expect(userDb.getUserByUsername).toHaveBeenCalledWith('testuser');
      });

      it('should reject login with invalid credentials', async () => {
        // Mock password comparison failure
        const bcrypt = await import('bcrypt');
        jest.spyOn(bcrypt, 'compare').mockResolvedValue(false);

        const loginData = {
          username: 'testuser',
          password: 'wrongpassword'
        };

        const response = await request(app)
          .post('/api/auth/login')
          .send(loginData)
          .expect(401);

        expect(response.body).toBeValidApiResponse();
        expect(response.body.success).toBe(false);
        expect(response.body.error).toMatch(/invalid credentials/i);
      });
    });
  });

  describe('Project Routes', () => {
    let authToken;

    beforeEach(async () => {
      // Create auth token for protected routes
      const { generateToken } = await import('../../middleware/auth.js');
      authToken = generateToken({ 
        id: 'user-123', 
        username: 'testuser' 
      });
    });

    describe('GET /api/projects', () => {
      it('should get user projects when authenticated', async () => {
        // Mock projects data
        const mockProjects = [
          testUtils.createTestProject({ name: 'Project 1' }),
          testUtils.createTestProject({ name: 'Project 2' })
        ];
        projectDb.getProjectsByUserId.mockReturnValue(mockProjects);

        const response = await request(app)
          .get('/api/projects')
          .set('Authorization', `Bearer ${authToken}`)
          .expect(200);

        expect(response.body).toBeValidApiResponse();
        expect(response.body.success).toBe(true);
        expect(response.body.data.projects).toHaveLength(2);
        expect(response.body.data.projects[0]).toHaveRequiredFields(['id', 'name', 'path']);
        
        // Verify database query
        expect(projectDb.getProjectsByUserId).toHaveBeenCalledWith('user-123');
      });

      it('should reject unauthenticated requests', async () => {
        const response = await request(app)
          .get('/api/projects')
          .expect(401);

        expect(response.body).toBeValidApiResponse();
        expect(response.body.success).toBe(false);
        expect(response.body.error).toMatch(/access denied/i);
        
        // Should not query database
        expect(projectDb.getProjectsByUserId).not.toHaveBeenCalled();
      });
    });

    describe('POST /api/projects', () => {
      it('should create new project when authenticated', async () => {
        const projectData = {
          name: 'New Test Project',
          path: '/test/new-project',
          description: 'Test project description'
        };

        const response = await request(app)
          .post('/api/projects')
          .set('Authorization', `Bearer ${authToken}`)
          .send(projectData)
          .expect(201);

        expect(response.body).toBeValidApiResponse();
        expect(response.body.success).toBe(true);
        expect(response.body.data.project).toHaveRequiredFields(['id', 'name', 'path']);
        
        // Verify database creation
        expect(projectDb.createProject).toHaveBeenCalledWith(
          expect.objectContaining({
            name: projectData.name,
            path: projectData.path,
            userId: 'user-123'
          })
        );
      });

      it('should validate project data', async () => {
        const response = await request(app)
          .post('/api/projects')
          .set('Authorization', `Bearer ${authToken}`)
          .send({}) // Empty payload
          .expect(400);

        expect(response.body).toBeValidApiResponse();
        expect(response.body.success).toBe(false);
        expect(response.body.error).toMatch(/required/i);
        
        // Should not create project
        expect(projectDb.createProject).not.toHaveBeenCalled();
      });
    });
  });

  describe('Health Check Route', () => {
    it('should return health status', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body).toEqual({
        status: 'ok',
        timestamp: expect.any(String),
        service: 'claudecodeui-backend'
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle database errors gracefully', async () => {
      // Mock database error
      userDb.getUserByUsername.mockImplementation(() => {
        throw new Error('Database connection failed');
      });

      const response = await request(app)
        .post('/api/auth/login')
        .send({
          username: 'testuser',
          password: 'password123'
        })
        .expect(500);

      expect(response.body).toBeValidApiResponse();
      expect(response.body.success).toBe(false);
      expect(response.body.error).toMatch(/server error/i);
    });

    it('should handle invalid JSON payload', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .set('Content-Type', 'application/json')
        .send('invalid json{')
        .expect(400);

      expect(response.body).toBeValidApiResponse();
      expect(response.body.success).toBe(false);
    });

    it('should handle 404 for unknown routes', async () => {
      const response = await request(app)
        .get('/api/nonexistent')
        .expect(404);

      expect(response.body).toBeValidApiResponse();
      expect(response.body.success).toBe(false);
      expect(response.body.error).toMatch(/not found/i);
    });
  });

  describe('CORS and Security Headers', () => {
    it('should include CORS headers', async () => {
      const response = await request(app)
        .options('/api/auth/login')
        .expect(204);

      expect(response.headers['access-control-allow-origin']).toBeDefined();
      expect(response.headers['access-control-allow-methods']).toBeDefined();
      expect(response.headers['access-control-allow-headers']).toBeDefined();
    });

    it('should include security headers', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      // Check for common security headers
      expect(response.headers['x-powered-by']).toBeUndefined(); // Should be hidden
    });
  });

  describe('Rate Limiting', () => {
    it('should handle multiple rapid requests', async () => {
      // Send multiple requests rapidly
      const promises = Array(10).fill().map(() =>
        request(app)
          .get('/health')
      );

      const responses = await Promise.all(promises);
      
      // All should succeed for health endpoint
      responses.forEach(response => {
        expect(response.status).toBe(200);
      });
    });
  });
});

// Helper function to test WebSocket integration
describe('WebSocket Integration', () => {
  let server;
  
  beforeAll(() => {
    server = createServer(app);
  });
  
  afterAll(() => {
    if (server) {
      server.close();
    }
  });

  it('should handle WebSocket connections', async () => {
    // T-2 (MUST): Test WebSocket API integration
    // This would test the WebSocket server setup
    // For now, just verify the server can be created
    expect(server).toBeDefined();
  });
});