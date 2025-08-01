/**
 * Jest Configuration for ClaudeCodeUI Backend
 * Following T-1 to T-5 coding guide testing principles
 */

export default {
  // Test environment
  testEnvironment: 'node',
  
  // ES Modules support
  preset: '@jest/preset-env',
  transform: {},
  extensionsToTreatAsEsm: ['.js'],
  globals: {
    'jest/globals': true
  },
  
  // Test file patterns - T-1: Colocate unit tests
  testMatch: [
    '**/*.spec.js',
    '**/tests/unit/**/*.test.js',
    '**/tests/integration/**/*.test.js'
  ],
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  
  // Coverage configuration
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html', 'json'],
  collectCoverageFrom: [
    '*.js',
    'routes/**/*.js',
    'middleware/**/*.js',
    'database/**/*.js',
    '!node_modules/**',
    '!coverage/**',
    '!tests/**',
    '!jest.config.js'
  ],
  
  // Coverage thresholds - T-2: Ensure quality gates
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 75,
      lines: 75,
      statements: 75
    },
    './routes/': {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  
  // Test timeout
  testTimeout: 15000,
  
  // Verbose output
  verbose: true,
  
  // Clear mocks between tests
  clearMocks: true,
  restoreMocks: true,
  
  // Module paths
  roots: ['<rootDir>'],
  
  // Test patterns to ignore
  testPathIgnorePatterns: [
    '/node_modules/',
    '/coverage/',
    '/dist/'
  ],
  
  // Watch plugins for better development experience
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname'
  ],
  
  // Test results processors
  reporters: [
    'default',
    ['jest-junit', {
      outputDirectory: 'coverage',
      outputName: 'junit.xml'
    }]
  ],
  
  // Module name mapping
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/$1',
    '^@routes/(.*)$': '<rootDir>/routes/$1',
    '^@middleware/(.*)$': '<rootDir>/middleware/$1',
    '^@database/(.*)$': '<rootDir>/database/$1'
  }
};