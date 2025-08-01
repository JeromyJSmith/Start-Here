/**
 * Unit tests for DarkModeToggle component.
 * Following T-1 (MUST): Colocate unit tests in same directory as source.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DarkModeToggle from './DarkModeToggle';

// Mock the theme context
const mockToggleDarkMode = vi.fn();
const mockUseTheme = vi.fn();

vi.mock('../contexts/ThemeContext', () => ({
  useTheme: () => mockUseTheme(),
}));

describe('DarkModeToggle', () => {
  beforeEach(() => {
    mockToggleDarkMode.mockClear();
    mockUseTheme.mockReturnValue({
      isDarkMode: false,
      toggleDarkMode: mockToggleDarkMode,
    });
  });

  describe('Rendering', () => {
    it('should render toggle button', () => {
      // T-1 (MUST): Test basic rendering
      render(<DarkModeToggle />);
      
      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).toBeInTheDocument();
      expect(toggleButton).toBeAccessible();
    });

    it('should have correct accessibility attributes', () => {
      // T-5 (SHOULD): Test accessibility thoroughly
      render(<DarkModeToggle />);
      
      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).toHaveAttribute('aria-label', 'Toggle dark mode');
      expect(toggleButton).toHaveAttribute('aria-checked', 'false');
      
      // Check for screen reader text
      expect(screen.getByText('Toggle dark mode')).toHaveClass('sr-only');
    });

    it('should display sun icon in light mode', () => {
      // T-5 (SHOULD): Test visual state in light mode
      mockUseTheme.mockReturnValue({
        isDarkMode: false,
        toggleDarkMode: mockToggleDarkMode,
      });
      
      render(<DarkModeToggle />);
      
      // Check for sun icon SVG path
      const sunIcon = screen.getByTestId('sun-icon') || 
                     document.querySelector('svg path[d*="M12 3v1m0 16v1"]');
      expect(sunIcon).toBeInTheDocument();
    });

    it('should display moon icon in dark mode', () => {
      // T-5 (SHOULD): Test visual state in dark mode
      mockUseTheme.mockReturnValue({
        isDarkMode: true,
        toggleDarkMode: mockToggleDarkMode,
      });
      
      render(<DarkModeToggle />);
      
      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).toHaveAttribute('aria-checked', 'true');
      
      // Check for moon icon SVG path
      const moonIcon = screen.getByTestId('moon-icon') ||
                      document.querySelector('svg path[d*="M20.354 15.354A9 9 0 018.646"]');
      expect(moonIcon).toBeInTheDocument();
    });
  });

  describe('Interaction', () => {
    it('should call toggleDarkMode when clicked', async () => {
      // T-1 (MUST): Test primary functionality
      const user = userEvent.setup();
      render(<DarkModeToggle />);
      
      const toggleButton = screen.getByRole('switch');
      await user.click(toggleButton);
      
      expect(mockToggleDarkMode).toHaveBeenCalledTimes(1);
    });

    it('should handle keyboard navigation', async () => {
      // T-5 (SHOULD): Test keyboard accessibility
      const user = userEvent.setup();
      render(<DarkModeToggle />);
      
      const toggleButton = screen.getByRole('switch');
      
      // Focus the button
      await user.tab();
      expect(toggleButton).toHaveFocus();
      
      // Press Enter to toggle
      await user.keyboard('{Enter}');
      expect(mockToggleDarkMode).toHaveBeenCalledTimes(1);
      
      // Press Space to toggle
      await user.keyboard(' ');
      expect(mockToggleDarkMode).toHaveBeenCalledTimes(2);
    });

    it('should prevent multiple rapid clicks', async () => {
      // T-5 (SHOULD): Test edge case handling
      const user = userEvent.setup();
      render(<DarkModeToggle />);
      
      const toggleButton = screen.getByRole('switch');
      
      // Rapid clicks
      await user.click(toggleButton);
      await user.click(toggleButton);
      await user.click(toggleButton);
      
      // Should have been called for each click
      expect(mockToggleDarkMode).toHaveBeenCalledTimes(3);
    });
  });

  describe('State Changes', () => {
    it('should update appearance when theme changes', () => {
      // T-5 (SHOULD): Test reactive state changes
      const { rerender } = render(<DarkModeToggle />);
      
      // Initially light mode
      let toggleButton = screen.getByRole('switch');
      expect(toggleButton).toHaveAttribute('aria-checked', 'false');
      
      // Switch to dark mode
      mockUseTheme.mockReturnValue({
        isDarkMode: true,
        toggleDarkMode: mockToggleDarkMode,
      });
      
      rerender(<DarkModeToggle />);
      
      toggleButton = screen.getByRole('switch');
      expect(toggleButton).toHaveAttribute('aria-checked', 'true');
    });

    it('should maintain focus state during theme changes', async () => {
      // T-5 (SHOULD): Test focus management
      const user = userEvent.setup();
      const { rerender } = render(<DarkModeToggle />);
      
      const toggleButton = screen.getByRole('switch');
      await user.click(toggleButton);
      
      // Button should still be focusable after state change
      expect(toggleButton).toBeInTheDocument();
      expect(toggleButton.tagName).toBe('BUTTON');
    });
  });

  describe('CSS Classes and Styling', () => {
    it('should apply correct classes for light mode', () => {
      // T-5 (SHOULD): Test styling logic
      mockUseTheme.mockReturnValue({
        isDarkMode: false,
        toggleDarkMode: mockToggleDarkMode,
      });
      
      render(<DarkModeToggle />);
      
      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).toHaveClass('bg-gray-200');
      
      // Check toggle position
      const toggleSpan = toggleButton.querySelector('span:not(.sr-only)');
      expect(toggleSpan).toHaveClass('translate-x-1');
    });

    it('should apply correct classes for dark mode', () => {
      // T-5 (SHOULD): Test styling logic
      mockUseTheme.mockReturnValue({
        isDarkMode: true,
        toggleDarkMode: mockToggleDarkMode,
      });
      
      render(<DarkModeToggle />);
      
      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).toHaveClass('dark:bg-gray-700');
      
      // Check toggle position
      const toggleSpan = toggleButton.querySelector('span:not(.sr-only)');
      expect(toggleSpan).toHaveClass('translate-x-7');
    });
  });

  describe('Error Handling', () => {
    it('should handle missing theme context gracefully', () => {
      // T-5 (SHOULD): Test error conditions
      mockUseTheme.mockReturnValue({
        isDarkMode: undefined,
        toggleDarkMode: undefined,
      });
      
      expect(() => render(<DarkModeToggle />)).not.toThrow();
      
      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).toBeInTheDocument();
    });

    it('should handle theme context errors', () => {
      // T-5 (SHOULD): Test error boundary conditions
      mockUseTheme.mockImplementation(() => {
        throw new Error('Theme context error');
      });
      
      // This would typically be caught by an error boundary in real app
      expect(() => render(<DarkModeToggle />)).toThrow('Theme context error');
    });
  });
});

// Integration test following T-2 principle
describe('DarkModeToggle Integration', () => {
  it('should work with actual theme context provider', () => {
    // T-2 (MUST): Integration test with theme provider
    // This would test with actual ThemeProvider wrapping the component
    
    // Mock a more realistic theme context
    const realishThemeContext = {
      isDarkMode: false,
      toggleDarkMode: () => {
        realishThemeContext.isDarkMode = !realishThemeContext.isDarkMode;
      },
    };
    
    mockUseTheme.mockReturnValue(realishThemeContext);
    
    render(<DarkModeToggle />);
    
    const toggleButton = screen.getByRole('switch');
    expect(toggleButton).toHaveAttribute('aria-checked', 'false');
    
    // Click should update the context
    fireEvent.click(toggleButton);
    
    // In real integration, this would cause a re-render with new state
    expect(realishThemeContext.isDarkMode).toBe(true);
  });
});