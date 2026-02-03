import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { DigitalHumansListPage } from '../ListPage';
import * as digitalHumanApi from '@/api/digitalHuman';
import type { DigitalHuman } from '@/types/digitalHuman';

// Mock the digital human API
vi.mock('@/api/digitalHuman', () => ({
  listDigitalHumans: vi.fn(),
  deleteDigitalHuman: vi.fn(),
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

describe('DigitalHumansListPage', () => {
  const mockDigitalHumans: DigitalHuman[] = [
    {
      id: 1,
      user_id: 1,
      name: 'Alice',
      description: 'A friendly AI assistant',
      image_path: '/images/alice.jpg',
      voice_model_path: '/models/alice_voice.pth',
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      user_id: 1,
      name: 'Bob',
      description: 'A professional presenter',
      is_active: true,
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    },
    {
      id: 3,
      user_id: 1,
      name: 'Charlie',
      is_active: true,
      created_at: '2024-01-03T00:00:00Z',
      updated_at: '2024-01-03T00:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementation
    vi.mocked(digitalHumanApi.listDigitalHumans).mockResolvedValue({
      digital_humans: mockDigitalHumans,
      total: mockDigitalHumans.length,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render page title', async () => {
      render(<DigitalHumansListPage />);

      expect(screen.getByText('Digital Humans')).toBeInTheDocument();
    });

    it('should render create button in header', async () => {
      render(<DigitalHumansListPage />);

      const createButton = screen.getByRole('button', { name: /create digital human/i });
      expect(createButton).toBeInTheDocument();
    });

    it('should load and display digital humans on mount', async () => {
      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(digitalHumanApi.listDigitalHumans).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
        expect(screen.getByText('Bob')).toBeInTheDocument();
        expect(screen.getByText('Charlie')).toBeInTheDocument();
      });
    });

    it('should display digital human descriptions', async () => {
      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('A friendly AI assistant')).toBeInTheDocument();
        expect(screen.getByText('A professional presenter')).toBeInTheDocument();
      });
    });

    it('should display "No description" for digital humans without description', async () => {
      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('No description')).toBeInTheDocument();
      });
    });

    it('should display creation dates', async () => {
      render(<DigitalHumansListPage />);

      await waitFor(() => {
        const dates = screen.getAllByText(/Created:/);
        expect(dates.length).toBeGreaterThanOrEqual(3);
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading spinner while fetching', () => {
      // Create a promise that never resolves to keep loading state
      let resolvePromise: any;
      const promise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      vi.mocked(digitalHumanApi.listDigitalHumans).mockReturnValue(promise as any);

      const { container } = render(<DigitalHumansListPage />);

      // Check for Ant Design Spin component
      const spinner = container.querySelector('.ant-spin');
      expect(spinner).toBeInTheDocument();

      // Clean up
      resolvePromise({ digital_humans: [], total: 0 });
    });
  });

  describe('Empty State', () => {
    it('should display empty state when no digital humans', async () => {
      vi.mocked(digitalHumanApi.listDigitalHumans).mockResolvedValue({
        digital_humans: [],
        total: 0,
      });

      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('No digital humans yet')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /create your first digital human/i })).toBeInTheDocument();
      });
    });

    it('should navigate to create page when clicking empty state button', async () => {
      const user = userEvent.setup();
      vi.mocked(digitalHumanApi.listDigitalHumans).mockResolvedValue({
        digital_humans: [],
        total: 0,
      });

      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('No digital humans yet')).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', { name: /create your first digital human/i });
      await user.click(createButton);

      expect(mockNavigate).toHaveBeenCalledWith('/digital-humans/create');
    });
  });

  describe('Navigation', () => {
    it('should navigate to create page when clicking header create button', async () => {
      const user = userEvent.setup();
      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', { name: /create digital human/i });
      await user.click(createButton);

      expect(mockNavigate).toHaveBeenCalledWith('/digital-humans/create');
    });

    it('should navigate to detail page when clicking card', async () => {
      const user = userEvent.setup();
      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
      });

      const card = screen.getByText('Alice').closest('.ant-card');
      expect(card).toBeInTheDocument();

      if (card) {
        await user.click(card);
        expect(mockNavigate).toHaveBeenCalledWith('/digital-humans/1');
      }
    });

    it('should navigate to generate page when clicking generate button', async () => {
      const user = userEvent.setup();
      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
      });

      const generateButtons = screen.getAllByRole('button', { name: /generate/i });
      await user.click(generateButtons[0]);

      expect(mockNavigate).toHaveBeenCalledWith('/digital-humans/1/generate');
    });
  });

  describe('Delete Functionality', () => {
    it('should show delete modal when clicking delete button', async () => {
      const user = userEvent.setup();
      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(screen.getByText('Delete Digital Human')).toBeInTheDocument();
        expect(screen.getByText(/Are you sure you want to delete/)).toBeInTheDocument();
      });
    });

    it('should close delete modal when clicking cancel', async () => {
      const user = userEvent.setup();
      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(screen.getByText('Delete Digital Human')).toBeInTheDocument();
      });

      // Find the Cancel button in the modal
      const buttons = screen.getAllByRole('button');
      const cancelButton = buttons.find(btn => btn.textContent === 'Cancel');
      expect(cancelButton).toBeDefined();

      if (cancelButton) {
        await user.click(cancelButton);

        // Wait a bit for the modal animation
        await new Promise(resolve => setTimeout(resolve, 500));

        // Verify the modal is hidden (check for open prop being false)
        await waitFor(() => {
          const modalRoot = document.querySelector('.ant-modal-root');
          if (modalRoot) {
            const modal = modalRoot.querySelector('.ant-modal-wrap');
            // Modal should either be gone or have display: none
            expect(modal?.getAttribute('style')).toContain('display: none');
          }
        }, { timeout: 3000 });
      }
    });

    it('should delete digital human when confirming', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');
      vi.mocked(digitalHumanApi.deleteDigitalHuman).mockResolvedValue();

      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(screen.getByText('Delete Digital Human')).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', { name: /^delete$/i });
      await user.click(confirmButton);

      await waitFor(() => {
        expect(digitalHumanApi.deleteDigitalHuman).toHaveBeenCalledWith(1);
        expect(message.success).toHaveBeenCalledWith('Digital human deleted successfully');
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message when fetch fails', async () => {
      const { message } = await import('antd');
      const errorMessage = 'Failed to fetch digital humans';
      vi.mocked(digitalHumanApi.listDigitalHumans).mockRejectedValue({
        response: { data: { detail: errorMessage } },
      });

      render(<DigitalHumansListPage />);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith(errorMessage);
      });
    });
  });
});
