import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { CreateDigitalHumanPage } from '../CreatePage';
import * as digitalHumanApi from '@/api/digitalHuman';

// Mock the digital human API
vi.mock('@/api/digitalHuman', () => ({
  createDigitalHuman: vi.fn(),
}));

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
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

describe('CreateDigitalHumanPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render page title', () => {
      render(<CreateDigitalHumanPage />);

      expect(screen.getByText('Create Digital Human')).toBeInTheDocument();
    });

    it('should render steps component', () => {
      const { container } = render(<CreateDigitalHumanPage />);

      const steps = container.querySelector('.ant-steps');
      expect(steps).toBeInTheDocument();
    });

    it('should render all three steps', () => {
      render(<CreateDigitalHumanPage />);

      expect(screen.getByText('Basic Info')).toBeInTheDocument();
      expect(screen.getByText('Upload Image')).toBeInTheDocument();
      expect(screen.getByText('Confirm')).toBeInTheDocument();
    });
  });

  describe('Step 1 - Basic Info', () => {
    it('should render name and description fields', () => {
      render(<CreateDigitalHumanPage />);

      expect(screen.getByPlaceholderText('Enter digital human name')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter a description (optional)')).toBeInTheDocument();
    });

    it('should show validation error for empty name', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      const nextButton = screen.getByRole('button', { name: /next/i });
      await user.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a name')).toBeInTheDocument();
      });
    });

    it('should show validation error for short name', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      const nameInput = screen.getByPlaceholderText('Enter digital human name');
      await user.type(nameInput, 'A');

      const nextButton = screen.getByRole('button', { name: /next/i });
      await user.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Name must be at least 2 characters')).toBeInTheDocument();
      });
    });

    it('should proceed to next step with valid name', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      const nameInput = screen.getByPlaceholderText('Enter digital human name');
      await user.type(nameInput, 'Test Digital Human');

      const nextButton = screen.getByRole('button', { name: /next/i });
      await user.click(nextButton);

      // Wait for step 2 content - check for upload text
      await waitFor(() => {
        expect(screen.getByText(/Upload an image/)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should allow optional description', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      const nameInput = screen.getByPlaceholderText('Enter digital human name');
      const descInput = screen.getByPlaceholderText('Enter a description (optional)');

      await user.type(nameInput, 'Test Digital Human');
      await user.type(descInput, 'This is a test description');

      const nextButton = screen.getByRole('button', { name: /next/i });
      await user.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText(/Upload an image/)).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Step 2 - Upload Image', () => {
    it('should render upload component', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      // Fill form and go to step 2
      const nameInput = screen.getByPlaceholderText('Enter digital human name');
      await user.type(nameInput, 'Test Digital Human');

      const nextButton = screen.getByRole('button', { name: /next/i });
      await user.click(nextButton);

      // Check for unique step 2 content
      await waitFor(() => {
        expect(screen.getByText(/Supported formats/)).toBeInTheDocument();
        expect(screen.getByText(/Upload an image/)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should show previous button on step 2', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      // Go to step 2
      const nameInput = screen.getByPlaceholderText('Enter digital human name');
      await user.type(nameInput, 'Test Digital Human');
      await user.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /previous/i })).toBeInTheDocument();
      });
    });

    it('should go back to step 1 when clicking previous', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      // Go to step 2
      const nameInput = screen.getByPlaceholderText('Enter digital human name');
      await user.type(nameInput, 'Test Digital Human');
      await user.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /previous/i })).toBeInTheDocument();
      });

      // Go back
      await user.click(screen.getByRole('button', { name: /previous/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Enter digital human name')).toBeInTheDocument();
      });
    });
  });

  describe('Step 3 - Confirm', () => {
    it('should display review information', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      // Fill form
      const nameInput = screen.getByPlaceholderText('Enter digital human name');
      const descInput = screen.getByPlaceholderText('Enter a description (optional)');
      await user.type(nameInput, 'Test Digital Human');
      await user.type(descInput, 'Test description');

      // Go to step 2
      await user.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByText(/Supported formats/)).toBeInTheDocument();
      }, { timeout: 3000 });

      // Go to step 3
      await user.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByText('Review Your Digital Human')).toBeInTheDocument();
      }, { timeout: 3000 });

      // Check if the values are displayed
      expect(screen.getByText('Test Digital Human')).toBeInTheDocument();
      expect(screen.getByText('Test description')).toBeInTheDocument();
    });

    it('should show create button on final step', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      // Navigate to final step
      const nameInput = screen.getByPlaceholderText('Enter digital human name');
      await user.type(nameInput, 'Test Digital Human');
      await user.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByText(/Supported formats/)).toBeInTheDocument();
      }, { timeout: 3000 });

      await user.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /^create$/i })).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Navigation', () => {
    it('should render cancel button on all steps', () => {
      render(<CreateDigitalHumanPage />);

      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });

    it('should navigate to list page when clicking cancel', async () => {
      const user = userEvent.setup();
      render(<CreateDigitalHumanPage />);

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      expect(mockNavigate).toHaveBeenCalledWith('/digital-humans');
    });
  });

  describe('Submission', () => {
    it('should create digital human and navigate to detail page', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');
      const mockDigitalHuman = {
        id: 1,
        user_id: 1,
        name: 'Test Digital Human',
        description: 'Test description',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(digitalHumanApi.createDigitalHuman).mockResolvedValue(mockDigitalHuman);

      render(<CreateDigitalHumanPage />);

      // Fill form
      const nameInput = screen.getByPlaceholderText('Enter digital human name');
      await user.type(nameInput, 'Test Digital Human');

      // Navigate to final step
      await user.click(screen.getByRole('button', { name: /next/i }));
      await waitFor(() => {
        expect(screen.getByText(/Supported formats/)).toBeInTheDocument();
      }, { timeout: 3000 });

      await user.click(screen.getByRole('button', { name: /next/i }));
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /^create$/i })).toBeInTheDocument();
      }, { timeout: 3000 });

      // Submit
      await user.click(screen.getByRole('button', { name: /^create$/i }));

      await waitFor(() => {
        expect(digitalHumanApi.createDigitalHuman).toHaveBeenCalled();
        expect(message.success).toHaveBeenCalledWith('Digital human created successfully!');
        expect(mockNavigate).toHaveBeenCalledWith('/digital-humans/1');
      }, { timeout: 3000 });
    });
  });
});
