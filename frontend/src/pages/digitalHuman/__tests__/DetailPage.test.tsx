import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { DigitalHumanDetailPage } from '../DetailPage';
import type { DigitalHuman } from '@/types/digitalHuman';

// Mock react-router-dom
const mockNavigate = vi.fn();
const mockParams = { id: '1' };
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => mockParams,
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
      info: vi.fn(),
    },
  };
});

// Mock the digital human store
const mockFetchDigitalHuman = vi.fn();
const mockDeleteDigitalHuman = vi.fn();
const mockClearError = vi.fn();

vi.mock('@/store/digitalHumanStore', () => ({
  useDigitalHumanStore: () => ({
    currentDigitalHuman: mockCurrentDigitalHuman,
    loading: mockLoading,
    error: mockError,
    fetchDigitalHuman: mockFetchDigitalHuman,
    deleteDigitalHuman: mockDeleteDigitalHuman,
    clearError: mockClearError,
  }),
}));

let mockCurrentDigitalHuman: DigitalHuman | null = null;
let mockLoading = false;
let mockError: string | null = null;

describe('DigitalHumanDetailPage', () => {
  const mockDigitalHuman: DigitalHuman = {
    id: 1,
    user_id: 1,
    name: 'Test Digital Human',
    description: 'Test description',
    image_path: '/images/test.jpg',
    voice_model_path: '/models/voice.pth',
    video_path: '/videos/test.mp4',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockCurrentDigitalHuman = null;
    mockLoading = false;
    mockError = null;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Loading State', () => {
    it('should show loading spinner while fetching', () => {
      mockLoading = true;
      const { container } = render(<DigitalHumanDetailPage />);

      const spinner = container.querySelector('.ant-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should call fetchDigitalHuman on mount', () => {
      render(<DigitalHumanDetailPage />);

      expect(mockFetchDigitalHuman).toHaveBeenCalledWith(1);
    });
  });

  describe('Not Found State', () => {
    it('should show not found message when digital human is null', () => {
      mockCurrentDigitalHuman = null;
      mockLoading = false;

      render(<DigitalHumanDetailPage />);

      expect(screen.getByText('Digital Human Not Found')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /back to list/i })).toBeInTheDocument();
    });

    it('should navigate to list when clicking back button in not found state', async () => {
      const user = userEvent.setup();
      mockCurrentDigitalHuman = null;
      mockLoading = false;

      render(<DigitalHumanDetailPage />);

      const backButton = screen.getByRole('button', { name: /back to list/i });
      await user.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith('/digital-humans');
    });
  });

  describe('Rendering Digital Human Details', () => {
    beforeEach(() => {
      mockCurrentDigitalHuman = mockDigitalHuman;
      mockLoading = false;
    });

    it('should render digital human name', () => {
      render(<DigitalHumanDetailPage />);

      // Check for the name in the title (h2 element)
      const heading = screen.getByRole('heading', { level: 2, name: 'Test Digital Human' });
      expect(heading).toBeInTheDocument();
    });

    it('should render back to list button', () => {
      render(<DigitalHumanDetailPage />);

      expect(screen.getByRole('button', { name: /back to list/i })).toBeInTheDocument();
    });

    it('should render action buttons', () => {
      render(<DigitalHumanDetailPage />);

      expect(screen.getByRole('button', { name: /generate video/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument();
    });

    it('should render all description fields', () => {
      render(<DigitalHumanDetailPage />);

      expect(screen.getByText('ID')).toBeInTheDocument();
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Description')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Image Path')).toBeInTheDocument();
      expect(screen.getByText('Voice Model Path')).toBeInTheDocument();
      expect(screen.getByText('Video Path')).toBeInTheDocument();
      expect(screen.getByText('Created At')).toBeInTheDocument();
      expect(screen.getByText('Updated At')).toBeInTheDocument();
    });

    it('should display digital human values', () => {
      render(<DigitalHumanDetailPage />);

      expect(screen.getByText('Test description')).toBeInTheDocument();
      expect(screen.getByText('Active')).toBeInTheDocument();
      expect(screen.getByText('/images/test.jpg')).toBeInTheDocument();
      expect(screen.getByText('/models/voice.pth')).toBeInTheDocument();
      expect(screen.getByText('/videos/test.mp4')).toBeInTheDocument();
    });

    it('should show "No description" when description is empty', () => {
      mockCurrentDigitalHuman = { ...mockDigitalHuman, description: undefined };

      render(<DigitalHumanDetailPage />);

      expect(screen.getByText('No description')).toBeInTheDocument();
    });

    it('should show "Inactive" when is_active is false', () => {
      mockCurrentDigitalHuman = { ...mockDigitalHuman, is_active: false };

      render(<DigitalHumanDetailPage />);

      expect(screen.getByText('Inactive')).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    beforeEach(() => {
      mockCurrentDigitalHuman = mockDigitalHuman;
      mockLoading = false;
    });

    it('should navigate to list when clicking back button', async () => {
      const user = userEvent.setup();
      render(<DigitalHumanDetailPage />);

      const backButton = screen.getByRole('button', { name: /back to list/i });
      await user.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith('/digital-humans');
    });

    it('should navigate to generate page when clicking generate button', async () => {
      const user = userEvent.setup();
      render(<DigitalHumanDetailPage />);

      const generateButton = screen.getByRole('button', { name: /generate video/i });
      await user.click(generateButton);

      expect(mockNavigate).toHaveBeenCalledWith('/digital-humans/1/generate');
    });

    it('should show info message when clicking edit button', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');

      render(<DigitalHumanDetailPage />);

      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      expect(message.info).toHaveBeenCalledWith('Edit functionality coming soon');
    });
  });

  describe('Delete Functionality', () => {
    beforeEach(() => {
      mockCurrentDigitalHuman = mockDigitalHuman;
      mockLoading = false;
    });

    it('should delete digital human and navigate to list', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');
      mockDeleteDigitalHuman.mockResolvedValue(undefined);

      render(<DigitalHumanDetailPage />);

      const deleteButton = screen.getByRole('button', { name: /delete/i });
      await user.click(deleteButton);

      await waitFor(() => {
        expect(mockDeleteDigitalHuman).toHaveBeenCalledWith(1);
        expect(message.success).toHaveBeenCalledWith('Digital human deleted successfully');
        expect(mockNavigate).toHaveBeenCalledWith('/digital-humans');
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message when error occurs', async () => {
      const { message } = await import('antd');
      mockError = 'Failed to fetch digital human';
      mockCurrentDigitalHuman = null;

      render(<DigitalHumanDetailPage />);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith('Failed to fetch digital human');
        expect(mockClearError).toHaveBeenCalled();
      });
    });
  });
});
