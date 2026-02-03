import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { LoginPage } from '../LoginPage';
import { useAuthStore } from '@/store/authStore';
import { ROUTES } from '@/utils/constants';

// Mock the auth store
vi.mock('@/store/authStore', () => ({
  useAuthStore: vi.fn(),
}));

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
      <a href={to}>{children}</a>
    ),
  };
});

// Mock antd message
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd');
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
    },
  };
});

describe('LoginPage', () => {
  const mockLogin = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();

    // Default mock implementation
    vi.mocked(useAuthStore).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      login: mockLogin,
      register: vi.fn(),
      logout: vi.fn(),
      checkAuth: vi.fn(),
      clearError: vi.fn(),
    });
  });

  describe('Rendering', () => {
    it('should render login form with all elements', () => {
      render(<LoginPage />);

      // Check title
      expect(screen.getByText('OpenUser')).toBeInTheDocument();
      expect(screen.getByText('Sign in to your account')).toBeInTheDocument();

      // Check form fields
      expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();

      // Check submit button
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();

      // Check sign up link
      expect(screen.getByText("Don't have an account?")).toBeInTheDocument();
      expect(screen.getByText('Sign up')).toBeInTheDocument();
    });

    it('should render loading state when isLoading is true', () => {
      vi.mocked(useAuthStore).mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: true,
        error: null,
        login: mockLogin,
        register: vi.fn(),
        logout: vi.fn(),
        checkAuth: vi.fn(),
        clearError: vi.fn(),
      });

      render(<LoginPage />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      expect(submitButton).toHaveClass('ant-btn-loading');
    });
  });

  describe('Form Validation', () => {
    it('should show validation error when username is empty', async () => {
      const user = userEvent.setup();
      render(<LoginPage />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please input your username!')).toBeInTheDocument();
      });
    });

    it('should show validation error when password is empty', async () => {
      const user = userEvent.setup();
      render(<LoginPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      await user.type(usernameInput, 'testuser');

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please input your password!')).toBeInTheDocument();
      });
    });

    it('should not show validation errors when both fields are filled', async () => {
      const user = userEvent.setup();
      mockLogin.mockResolvedValue(undefined);

      render(<LoginPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const passwordInput = screen.getByPlaceholderText('Password');

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'Test123!');

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.queryByText('Please input your username!')).not.toBeInTheDocument();
        expect(screen.queryByText('Please input your password!')).not.toBeInTheDocument();
      });
    });
  });

  describe('Login Functionality', () => {
    it('should call login with correct credentials', async () => {
      const user = userEvent.setup();
      mockLogin.mockResolvedValue(undefined);

      render(<LoginPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const passwordInput = screen.getByPlaceholderText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'Test123!');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          username: 'testuser',
          password: 'Test123!',
        });
      });
    });

    it('should navigate to dashboard on successful login', async () => {
      const user = userEvent.setup();
      mockLogin.mockResolvedValue(undefined);

      render(<LoginPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const passwordInput = screen.getByPlaceholderText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'Test123!');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith(ROUTES.DASHBOARD);
      });
    });

    it('should show success message on successful login', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');
      mockLogin.mockResolvedValue(undefined);

      render(<LoginPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const passwordInput = screen.getByPlaceholderText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'Test123!');
      await user.click(submitButton);

      await waitFor(() => {
        expect(message.success).toHaveBeenCalledWith('Login successful!');
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message on login failure', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');
      const errorMessage = 'Invalid credentials';
      mockLogin.mockRejectedValue(new Error(errorMessage));

      render(<LoginPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const passwordInput = screen.getByPlaceholderText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(submitButton);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith(errorMessage);
      });
    });

    it('should show generic error message when error is not an Error instance', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');
      mockLogin.mockRejectedValue('Unknown error');

      render(<LoginPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const passwordInput = screen.getByPlaceholderText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'Test123!');
      await user.click(submitButton);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith('Login failed. Please check your credentials.');
      });
    });

    it('should not navigate on login failure', async () => {
      const user = userEvent.setup();
      mockLogin.mockRejectedValue(new Error('Invalid credentials'));

      render(<LoginPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const passwordInput = screen.getByPlaceholderText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalled();
      });

      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Navigation', () => {
    it('should have link to registration page', () => {
      render(<LoginPage />);

      const signUpLink = screen.getByText('Sign up');
      expect(signUpLink).toHaveAttribute('href', ROUTES.REGISTER);
    });
  });

  describe('Accessibility', () => {
    it('should have proper form structure', () => {
      render(<LoginPage />);

      // Ant Design Form doesn't use native form role, check for form element
      const forms = document.querySelectorAll('form');
      expect(forms.length).toBeGreaterThan(0);
    });

    it('should have submit button with proper type', () => {
      render(<LoginPage />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      expect(submitButton).toHaveAttribute('type', 'submit');
    });
  });
});
