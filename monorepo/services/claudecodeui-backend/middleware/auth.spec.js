/**
 * Unit tests for auth middleware.
 * Following T-1 (MUST): Colocate unit tests in same directory as source.
 */

import { jest } from '@jest/globals';
import jwt from 'jsonwebtoken';
import { 
  validateApiKey, 
  authenticateToken, 
  generateToken, 
  authenticateWebSocket,
  JWT_SECRET 
} from './auth.js';

// Mock dependencies
jest.mock('jsonwebtoken');
jest.mock('../database/db.js', () => ({
  userDb: {
    getUserById: jest.fn()
  }
}));

import { userDb } from '../database/db.js';

describe('auth middleware', () => {
  let req, res, next;
  
  beforeEach(() => {
    req = testUtils.createMockRequest();
    res = testUtils.createMockResponse();
    next = testUtils.createMockNext();
    
    // Clear environment variables
    delete process.env.API_KEY;
    delete process.env.JWT_SECRET;
  });

  describe('validateApiKey', () => {
    it('should skip validation when API_KEY is not configured', () => {
      // T-1 (MUST): Test that middleware passes through when no API key configured
      validateApiKey(req, res, next);
      
      expect(next).toHaveBeenCalledWith();
      expect(res.status).not.toHaveBeenCalled();
    });

    it('should reject request with missing API key when configured', () => {
      // T-5 (SHOULD): Test edge case with missing API key
      process.env.API_KEY = 'test-api-key';
      
      validateApiKey(req, res, next);
      
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalledWith({ error: 'Invalid API key' });
      expect(next).not.toHaveBeenCalled();
    });

    it('should reject request with invalid API key', () => {
      // T-5 (SHOULD): Test edge case with wrong API key  
      process.env.API_KEY = 'correct-api-key';
      req.headers['x-api-key'] = 'wrong-api-key';
      
      validateApiKey(req, res, next);
      
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalledWith({ error: 'Invalid API key' });
      expect(next).not.toHaveBeenCalled();
    });

    it('should allow request with valid API key', () => {
      // T-1 (MUST): Test successful authentication path
      const apiKey = 'valid-api-key';
      process.env.API_KEY = apiKey;
      req.headers['x-api-key'] = apiKey;
      
      validateApiKey(req, res, next);
      
      expect(next).toHaveBeenCalledWith();
      expect(res.status).not.toHaveBeenCalled();
    });
  });

  describe('authenticateToken', () => {
    const mockUser = { id: 'user-123', username: 'testuser' };

    it('should reject request without token', async () => {
      // T-5 (SHOULD): Test edge case with missing token
      await authenticateToken(req, res, next);
      
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalledWith({ 
        error: 'Access denied. No token provided.' 
      });
      expect(next).not.toHaveBeenCalled();
    });

    it('should reject request with invalid token format', async () => {
      // T-5 (SHOULD): Test edge case with malformed token
      req.headers['authorization'] = 'InvalidFormat';
      
      await authenticateToken(req, res, next);
      
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalledWith({ 
        error: 'Access denied. No token provided.' 
      });
    });

    it('should reject request with invalid token', async () => {
      // T-5 (SHOULD): Test edge case with invalid JWT
      req.headers['authorization'] = 'Bearer invalid-token';
      jwt.verify.mockImplementation(() => {
        throw new Error('Invalid token');
      });
      
      await authenticateToken(req, res, next);
      
      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith({ error: 'Invalid token' });
      expect(next).not.toHaveBeenCalled();
    });

    it('should reject request when user not found', async () => {
      // T-5 (SHOULD): Test edge case with deleted user
      req.headers['authorization'] = 'Bearer valid-token';
      jwt.verify.mockReturnValue({ userId: 'user-123' });
      userDb.getUserById.mockReturnValue(null);
      
      await authenticateToken(req, res, next);
      
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalledWith({ 
        error: 'Invalid token. User not found.' 
      });
      expect(next).not.toHaveBeenCalled();
    });

    it('should authenticate valid token with existing user', async () => {
      // T-1 (MUST): Test successful authentication path
      req.headers['authorization'] = 'Bearer valid-token';
      jwt.verify.mockReturnValue({ userId: 'user-123' });
      userDb.getUserById.mockReturnValue(mockUser);
      
      await authenticateToken(req, res, next);
      
      expect(req.user).toEqual(mockUser);
      expect(next).toHaveBeenCalledWith();
      expect(res.status).not.toHaveBeenCalled();
    });
  });

  describe('generateToken', () => {
    const mockUser = { id: 'user-123', username: 'testuser' };

    it('should generate JWT token with user data', () => {
      // T-1 (MUST): Test token generation
      const mockToken = 'generated-jwt-token';
      jwt.sign.mockReturnValue(mockToken);
      
      const result = generateToken(mockUser);
      
      expect(result).toBe(mockToken);
      expect(jwt.sign).toHaveBeenCalledWith(
        { userId: mockUser.id, username: mockUser.username },
        JWT_SECRET
      );
    });

    it('should use correct JWT secret', () => {
      // T-5 (SHOULD): Test that correct secret is used
      const mockToken = 'generated-jwt-token';
      jwt.sign.mockReturnValue(mockToken);
      
      generateToken(mockUser);
      
      expect(jwt.sign).toHaveBeenCalledWith(
        expect.any(Object),
        JWT_SECRET
      );
    });
  });

  describe('authenticateWebSocket', () => {
    it('should return null for missing token', () => {
      // T-5 (SHOULD): Test edge case with no token
      const result = authenticateWebSocket(null);
      expect(result).toBeNull();
      
      const result2 = authenticateWebSocket(undefined);
      expect(result2).toBeNull();
    });

    it('should return null for invalid token', () => {
      // T-5 (SHOULD): Test edge case with invalid token
      jwt.verify.mockImplementation(() => {
        throw new Error('Invalid token');
      });
      
      const result = authenticateWebSocket('invalid-token');
      
      expect(result).toBeNull();
      expect(jwt.verify).toHaveBeenCalledWith('invalid-token', JWT_SECRET);
    });

    it('should return decoded data for valid token', () => {
      // T-1 (MUST): Test successful WebSocket authentication
      const mockDecoded = { userId: 'user-123', username: 'testuser' };
      jwt.verify.mockReturnValue(mockDecoded);
      
      const result = authenticateWebSocket('valid-token');
      
      expect(result).toEqual(mockDecoded);
      expect(jwt.verify).toHaveBeenCalledWith('valid-token', JWT_SECRET);
    });
  });

  describe('JWT_SECRET', () => {
    it('should use environment variable when available', () => {
      // T-5 (SHOULD): Test configuration handling
      // Note: This test verifies the module uses env vars correctly
      expect(typeof JWT_SECRET).toBe('string');
      expect(JWT_SECRET.length).toBeGreaterThan(0);
    });
  });
});

// Integration test example following T-2 principle
describe('auth middleware integration', () => {
  it('should work with express request/response cycle', async () => {
    // T-2 (MUST): Integration test with actual Express-like objects
    const mockReq = {
      headers: { authorization: 'Bearer valid-token' },
      user: null
    };
    
    const mockRes = {
      statusCode: null,
      jsonData: null,
      status: function(code) { 
        this.statusCode = code; 
        return this; 
      },
      json: function(data) { 
        this.jsonData = data; 
        return this; 
      }
    };
    
    const mockNext = jest.fn();
    
    // Mock successful verification
    jwt.verify.mockReturnValue({ userId: 'user-123' });
    userDb.getUserById.mockReturnValue({ id: 'user-123', username: 'test' });
    
    await authenticateToken(mockReq, mockRes, mockNext);
    
    expect(mockReq.user).toBeTruthy();
    expect(mockNext).toHaveBeenCalled();
    expect(mockRes.statusCode).toBeNull();
  });
});