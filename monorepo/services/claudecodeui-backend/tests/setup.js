/**
 * Jest setup configuration for ClaudeCodeUI Backend
 * Following T-1 to T-5 coding guide principles
 */

const { jest } = require('@jest/globals');

// Global test setup
beforeAll(async () => {
  // Set test environment variables
  process.env.NODE_ENV = 'test';
  process.env.DATABASE_URL = 'sqlite::memory:';
  process.env.JWT_SECRET = 'test-secret-key-for-testing-only';
  process.env.PORT = '3001';
  
  // Mock external services
  global.mockDatabase = {
    run: jest.fn().mockResolvedValue({ changes: 1 }),
    get: jest.fn().mockResolvedValue(null),
    all: jest.fn().mockResolvedValue([]),
    close: jest.fn().mockResolvedValue()
  };
  
  // Mock authentication
  global.mockAuth = {
    verifyToken: jest.fn().mockResolvedValue({ userId: 'test-user' }),
    generateToken: jest.fn().mockReturnValue('mock-jwt-token'),
    hashPassword: jest.fn().mockResolvedValue('hashed-password'),
    comparePassword: jest.fn().mockResolvedValue(true)
  };
  
  // Mock file system operations
  global.mockFS = {
    readFile: jest.fn().mockResolvedValue('file content'),
    writeFile: jest.fn().mockResolvedValue(),
    access: jest.fn().mockResolvedValue(),
    mkdir: jest.fn().mockResolvedValue(),
    readdir: jest.fn().mockResolvedValue([])
  };
  
  // Mock git operations  
  global.mockGit = {
    status: jest.fn().mockResolvedValue({ modified: [], staged: [] }),
    add: jest.fn().mockResolvedValue(),
    commit: jest.fn().mockResolvedValue(),
    push: jest.fn().mockResolvedValue(),
    pull: jest.fn().mockResolvedValue()
  };
});

// Clean up after each test
afterEach(() => {
  // Clear all mocks
  jest.clearAllMocks();
  
  // Reset mock implementations
  if (global.mockDatabase) {
    global.mockDatabase.run.mockResolvedValue({ changes: 1 });
    global.mockDatabase.get.mockResolvedValue(null);
    global.mockDatabase.all.mockResolvedValue([]);
  }
});

// Global test utilities
global.testUtils = {
  /**
   * Create mock request object
   */
  createMockRequest: (overrides = {}) => ({
    body: {},
    params: {},
    query: {},
    headers: {},
    user: null,
    ...overrides
  }),
  
  /**
   * Create mock response object
   */
  createMockResponse: () => {
    const res = {};
    res.status = jest.fn().mockReturnValue(res);
    res.json = jest.fn().mockReturnValue(res);
    res.send = jest.fn().mockReturnValue(res);
    res.cookie = jest.fn().mockReturnValue(res);
    res.clearCookie = jest.fn().mockReturnValue(res);
    return res;
  },
  
  /**
   * Create mock Express next function
   */
  createMockNext: () => jest.fn(),
  
  /**
   * Wait for specified milliseconds
   */
  waitFor: (ms) => new Promise(resolve => setTimeout(resolve, ms)),
  
  /**
   * Generate test project data
   */
  createTestProject: (overrides = {}) => ({
    id: 'test-project-123',
    name: 'Test Project',
    path: '/test/path',
    description: 'Test project description',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides
  }),
  
  /**
   * Generate test user data
   */
  createTestUser: (overrides = {}) => ({
    id: 'test-user-123',
    username: 'testuser',
    email: 'test@example.com',
    created_at: new Date().toISOString(),
    ...overrides
  }),
  
  /**
   * Generate test API key data
   */
  createTestApiKey: (overrides = {}) => ({
    id: 'api-key-123',
    name: 'Test API Key',
    key: 'test-api-key-value',
    created_at: new Date().toISOString(),
    last_used: null,
    ...overrides
  })
};

// Custom matchers
expect.extend({
  /**
   * Check if response has correct structure
   */
  toBeValidApiResponse(received) {
    const pass = received && 
                 typeof received === 'object' &&
                 ('success' in received || 'error' in received);
    
    if (pass) {
      return {
        message: () => `expected ${JSON.stringify(received)} not to be valid API response`,
        pass: true
      };
    } else {
      return {
        message: () => `expected ${JSON.stringify(received)} to be valid API response with 'success' or 'error' field`,
        pass: false
      };
    }
  },
  
  /**
   * Check if object has required fields
   */
  toHaveRequiredFields(received, fields) {
    const missingFields = fields.filter(field => !(field in received));
    const pass = missingFields.length === 0;
    
    if (pass) {
      return {
        message: () => `expected ${JSON.stringify(received)} not to have required fields ${fields.join(', ')}`,
        pass: true
      };
    } else {
      return {
        message: () => `expected ${JSON.stringify(received)} to have required fields: ${missingFields.join(', ')}`,
        pass: false
      };
    }
  }
});

// Mock console methods to reduce test noise
global.console = {
  ...console,
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  info: jest.fn(),
  debug: jest.fn()
};