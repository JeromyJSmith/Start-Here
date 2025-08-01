/**
 * Vitest configuration for ClaudeCodeUI Frontend
 * Following T-1 to T-5 coding guide testing principles
 */

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  
  test: {
    // Test environment
    environment: 'jsdom',
    
    // Test file patterns - T-1: Colocate unit tests
    include: [
      '**/*.{test,spec}.{js,jsx,ts,tsx}',
      'src/**/*.spec.{js,jsx,ts,tsx}'
    ],
    
    // Setup files
    setupFiles: ['./src/test/setup.js'],
    
    // Globals for React Testing Library
    globals: true,
    
    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: [
        'src/**/*.{js,jsx,ts,tsx}'
      ],
      exclude: [
        'src/**/*.{test,spec}.{js,jsx,ts,tsx}',
        'src/test/**',
        'src/**/*.d.ts',
        'src/main.jsx',
        'src/index.css',
        'node_modules/**'
      ],
      // Coverage thresholds - T-2: Quality gates
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70
        },
        'src/components/': {
          branches: 75,
          functions: 75,
          lines: 75,
          statements: 75
        }
      }
    },
    
    // Test timeout
    testTimeout: 10000,
    
    // Watch options
    watch: {
      ignored: ['**/node_modules/**', '**/dist/**']
    }
  },
  
  // Resolve aliases
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@components': resolve(__dirname, './src/components'),
      '@contexts': resolve(__dirname, './src/contexts'),
      '@hooks': resolve(__dirname, './src/hooks'),
      '@utils': resolve(__dirname, './src/utils'),
      '@lib': resolve(__dirname, './src/lib')
    }
  }
});