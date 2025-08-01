/**
 * Test setup for ClaudeCodeUI Frontend
 * Following T-1 to T-5 coding guide testing principles
 */

import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Global test cleanup
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn(() => ({
  disconnect: vi.fn(),
  observe: vi.fn(),
  unobserve: vi.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = vi.fn(() => ({
  disconnect: vi.fn(),
  observe: vi.fn(),
  unobserve: vi.fn(),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock WebSocket
global.WebSocket = vi.fn(() => ({
  close: vi.fn(),
  send: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  readyState: 1, // OPEN
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
}));

// Mock fetch
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
    blob: () => Promise.resolve(new Blob()),
  })
);

// Mock URL.createObjectURL
global.URL.createObjectURL = vi.fn(() => 'mocked-url');
global.URL.revokeObjectURL = vi.fn();

// Mock File and FileReader
global.FileReader = vi.fn(() => ({
  readAsText: vi.fn(),
  readAsDataURL: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  result: null,
  error: null,
  readyState: 0,
}));

// Mock clipboard API
Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: vi.fn(() => Promise.resolve()),
    readText: vi.fn(() => Promise.resolve('')),
  },
});

// Mock CodeMirror
vi.mock('@uiw/react-codemirror', () => ({
  default: vi.fn(({ value, onChange }) => {
    return {
      type: 'div',
      props: {
        'data-testid': 'codemirror',
        children: value,
        onClick: () => onChange && onChange('mock-change'),
      },
    };
  }),
}));

// Mock xterm
vi.mock('xterm', () => ({
  Terminal: vi.fn(() => ({
    open: vi.fn(),
    write: vi.fn(),
    writeln: vi.fn(),
    clear: vi.fn(),
    dispose: vi.fn(),
    onData: vi.fn(),
    onResize: vi.fn(),
    loadAddon: vi.fn(),
    fit: vi.fn(),
  })),
}));

// Global test utilities
global.testUtils = {
  /**
   * Create mock user data
   */
  createMockUser: (overrides = {}) => ({
    id: 'user-123',
    username: 'testuser',
    email: 'test@example.com',
    ...overrides,
  }),

  /**
   * Create mock project data
   */
  createMockProject: (overrides = {}) => ({
    id: 'project-123',
    name: 'Test Project',
    path: '/test/path',
    description: 'Test project description',
    ...overrides,
  }),

  /**
   * Create mock conversation data
   */
  createMockConversation: (overrides = {}) => ({
    id: 'conv-123',
    title: 'Test Conversation',
    messages: [],
    createdAt: new Date().toISOString(),
    ...overrides,
  }),

  /**
   * Create mock API response
   */
  createMockApiResponse: (data = {}, success = true) => ({
    success,
    data: success ? data : undefined,
    error: success ? undefined : data.message || 'Test error',
  }),

  /**
   * Wait for next tick
   */
  waitFor: (ms = 0) => new Promise(resolve => setTimeout(resolve, ms)),

  /**
   * Simulate user typing
   */
  simulateTyping: async (user, input, text) => {
    await user.clear(input);
    await user.type(input, text);
  },

  /**
   * Mock API calls
   */
  mockApiCall: (endpoint, response, status = 200) => {
    global.fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        json: () => Promise.resolve(response),
        text: () => Promise.resolve(JSON.stringify(response)),
      })
    );
  },
};

// Custom matchers
expect.extend({
  /**
   * Check if element has correct accessibility attributes
   */
  toBeAccessible(received) {
    const hasRole = received.getAttribute('role');
    const hasAriaLabel = received.getAttribute('aria-label') || received.getAttribute('aria-labelledby');
    
    const pass = hasRole || hasAriaLabel || received.tagName.toLowerCase() === 'button';
    
    if (pass) {
      return {
        message: () => `expected element not to be accessible`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected element to have role or aria-label for accessibility`,
        pass: false,
      };
    }
  },

  /**
   * Check if component is properly memoized
   */
  toBeProperlyMemoized(received) {
    const displayName = received.displayName || received.name;
    const pass = displayName && (
      displayName.includes('Memo') || 
      displayName.includes('memo') ||
      received.$$typeof?.toString().includes('memo')
    );
    
    if (pass) {
      return {
        message: () => `expected component not to be memoized`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected component to be properly memoized for performance`,
        pass: false,
      };
    }
  },
});