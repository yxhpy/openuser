import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { RegisterPage } from '../RegisterPage';
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

describe('RegisterPage', () => {
  const mockRegister = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();

    vi.mocked(useAuthStore).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      login: vi.fn(),
      register: mockRegister,
      logout: vi.fn(),
      checkAuth: vi.fn(),
      clearError: vi.fn(),
    });
  });

  describe('Rendering', () => {
    it('should render registration form with all elements', () => {
      render(<RegisterPage />);

      expect(screen.getByText('OpenUser')).toBeInTheDocument();
      expect(screen.getByText('Create your account')).toBeInTheDocument();

      expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Confirm Password')).toBeInTheDocument();

      expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();

      expect(screen.getByText('Already have an account?')).toBeInTheDocument();
      expect(screen.getByText('Sign in')).toBeInTheDocument();
    });
  });

  describe('Form Validation - Username', () => {
    it('should show error when username is empty', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please input your username!')).toBeInTheDocument();
      });
    });

    it('should show error when username is too short', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      await user.type(usernameInput, 'ab');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Username must be at least 3 characters!')).toBeInTheDocument();
      });
    });
  });

  describe('Form Validation - Email', () => {
    it('should show error when email is empty', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      await user.type(usernameInput, 'testuser');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please input your email!')).toBeInTheDocument();
      });
    });

    it('should show error when email is invalid', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const emailInput = screen.getByPlaceholderText('Email');
      await user.type(emailInput, 'invalid-email');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email!')).toBeInTheDocument();
      });
    });
  });

  describe('Form Validation - Password', () => {
    it('should show error when password is empty', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const emailInput = screen.getByPlaceholderText('Email');

      await user.type(usernameInput, 'testuser');
      await user.type(emailInput, 'test@example.com');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please input your password!')).toBeInTheDocument();
      });
    });

    it('should show error when password is too short', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const passwordInput = screen.getByPlaceholderText('Password');
      await user.type(passwordInput, 'Test1');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 8 characters!')).toBeInTheDocument();
      });
    });

    it('should show error when password lacks uppercase letter', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const passwordInput = screen.getByPlaceholderText('Password');
      await user.type(passwordInput, 'test1234');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must contain at least one uppercase letter!')).toBeInTheDocument();
      });
    });

    it('should show error when password lacks lowercase letter', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const passwordInput = screen.getByPlaceholderText('Password');
      await user.type(passwordInput, 'TEST1234');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must contain at least one lowercase letter!')).toBeInTheDocument();
      });
    });

    it('should show error when password lacks digit', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const passwordInput = screen.getByPlaceholderText('Password');
      await user.type(passwordInput, 'TestPassword');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must contain at least one digit!')).toBeInTheDocument();
      });
    });

    it('should accept valid password', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const passwordInput = screen.getByPlaceholderText('Password');
      await user.type(passwordInput, 'Test1234');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.queryByText(/Password must/)).not.toBeInTheDocument();
      });
    });
  });

  describe('Form Validation - Confirm Password', () => {
    it('should show error when confirm password is empty', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const emailInput = screen.getByPlaceholderText('Email');
      const passwordInput = screen.getByPlaceholderText('Password');

      await user.type(usernameInput, 'testuser');
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'Test1234');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please confirm your password!')).toBeInTheDocument();
      });
    });

    it('should show error when passwords do not match', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const passwordInput = screen.getByPlaceholderText('Password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm Password');

      await user.type(passwordInput, 'Test1234');
      await user.type(confirmPasswordInput, 'Test5678');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match!')).toBeInTheDocument();
      });
    });
  });

  describe('Registration Functionality', () => {
    it('should call register with correct data', async () => {
      const user = userEvent.setup();
      mockRegister.mockResolvedValue(undefined);

      render(<RegisterPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const emailInput = screen.getByPlaceholderText('Email');
      const passwordInput = screen.getByPlaceholderText('Password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm Password');
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await user.type(usernameInput, 'testuser');
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'Test1234');
      await user.type(confirmPasswordInput, 'Test1234');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          username: 'testuser',
          email: 'test@example.com',
          password: 'Test1234',
          confirmPassword: 'Test1234',
        });
      });
    });

    it('should navigate to dashboard on successful registration', async () => {
      const user = userEvent.setup();
      mockRegister.mockResolvedValue(undefined);

      render(<RegisterPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const emailInput = screen.getByPlaceholderText('Email');
      const passwordInput = screen.getByPlaceholderText('Password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm Password');
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await user.type(usernameInput, 'testuser');
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'Test1234');
      await user.type(confirmPasswordInput, 'Test1234');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith(ROUTES.DASHBOARD);
      });
    });

    it('should show success message on successful registration', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');
      mockRegister.mockResolvedValue(undefined);

      render(<RegisterPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const emailInput = screen.getByPlaceholderText('Email');
      const passwordInput = screen.getByPlaceholderText('Password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm Password');
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await user.type(usernameInput, 'testuser');
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'Test1234');
      await user.type(confirmPasswordInput, 'Test1234');
      await user.click(submitButton);

      await waitFor(() => {
        expect(message.success).toHaveBeenCalledWith('Registration successful!');
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message on registration failure', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');
      const errorMessage = 'Username already exists';
      mockRegister.mockRejectedValue(new Error(errorMessage));

      render(<RegisterPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const emailInput = screen.getByPlaceholderText('Email');
      const passwordInput = screen.getByPlaceholderText('Password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm Password');
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await user.type(usernameInput, 'existinguser');
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'Test1234');
      await user.type(confirmPasswordInput, 'Test1234');
      await user.click(submitButton);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith(errorMessage);
      });
    });

    it('should not navigate on registration failure', async () => {
      const user = userEvent.setup();
      mockRegister.mockRejectedValue(new Error('Registration failed'));

      render(<RegisterPage />);

      const usernameInput = screen.getByPlaceholderText('Username');
      const emailInput = screen.getByPlaceholderText('Email');
      const passwordInput = screen.getByPlaceholderText('Password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm Password');
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await user.type(usernameInput, 'testuser');
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'Test1234');
      await user.type(confirmPasswordInput, 'Test1234');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalled();
      });

      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Navigation', () => {
    it('should have link to login page', () => {
      render(<RegisterPage />);

      const signInLink = screen.getByText('Sign in');
      expect(signInLink).toHaveAttribute('href', ROUTES.LOGIN);
    });
  });
});
