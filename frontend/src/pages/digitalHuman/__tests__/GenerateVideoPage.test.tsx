import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { GenerateVideoPage } from '../GenerateVideoPage';
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
    },
  };
});

// Mock the digital human store
const mockFetchDigitalHuman = vi.fn();
const mockGenerateVideo = vi.fn();
const mockClearError = vi.fn();

vi.mock('@/store/digitalHumanStore', () => ({
  useDigitalHumanStore: () => ({
    currentDigitalHuman: mockCurrentDigitalHuman,
    loading: mockLoading,
    error: mockError,
    fetchDigitalHuman: mockFetchDigitalHuman,
    generateVideo: mockGenerateVideo,
    clearError: mockClearError,
  }),
}));

let mockCurrentDigitalHuman: DigitalHuman | null = null;
let mockLoading = false;
let mockError: string | null = null;

describe('GenerateVideoPage', () => {
  const mockDigitalHuman: DigitalHuman = {
    id: 1,
    user_id: 1,
    name: 'Test Digital Human',
    description: 'Test description',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockCurrentDigitalHuman = mockDigitalHuman;
    mockLoading = false;
    mockError = null;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Loading and Not Found States', () => {
    it('should show loading spinner while fetching', () => {
      mockCurrentDigitalHuman = null;
      mockLoading = true;
      const { container } = render(<GenerateVideoPage />);

      const spinner = container.querySelector('.ant-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should show not found message when digital human is null', () => {
      mockCurrentDigitalHuman = null;
      mockLoading = false;

      render(<GenerateVideoPage />);

      expect(screen.getByText('Digital Human Not Found')).toBeInTheDocument();
    });

    it('should call fetchDigitalHuman on mount', () => {
      render(<GenerateVideoPage />);

      expect(mockFetchDigitalHuman).toHaveBeenCalledWith(1);
    });
  });

  describe('Rendering', () => {
    it('should render page title with digital human name', () => {
      render(<GenerateVideoPage />);

      expect(screen.getByText(/Generate Video - Test Digital Human/)).toBeInTheDocument();
    });

    it('should render back to detail button', () => {
      render(<GenerateVideoPage />);

      expect(screen.getByRole('button', { name: /back to detail/i })).toBeInTheDocument();
    });

    it('should render input type radio buttons', () => {
      render(<GenerateVideoPage />);

      // Check for radio buttons by role
      expect(screen.getByRole('radio', { name: /^text$/i })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: /audio file/i })).toBeInTheDocument();
    });

    it('should render text input by default', () => {
      render(<GenerateVideoPage />);

      expect(screen.getByPlaceholderText(/Enter the text you want the digital human to speak/)).toBeInTheDocument();
    });

    it('should render generation mode select', () => {
      render(<GenerateVideoPage />);

      expect(screen.getByText('Generation Mode')).toBeInTheDocument();
    });

    it('should render generate and cancel buttons', () => {
      render(<GenerateVideoPage />);

      expect(screen.getByRole('button', { name: /generate video/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });
  });

  describe('Input Type Switching', () => {
    it('should switch to audio input when audio button is clicked', async () => {
      const user = userEvent.setup();
      render(<GenerateVideoPage />);

      // Click on the label text instead of the radio button
      const audioLabel = screen.getByText('Audio File');
      await user.click(audioLabel);

      await waitFor(() => {
        expect(screen.getByText(/Upload an audio file/)).toBeInTheDocument();
      });
    });

    it('should switch back to text input when text button is clicked', async () => {
      const user = userEvent.setup();
      render(<GenerateVideoPage />);

      // Switch to audio
      const audioLabel = screen.getByText('Audio File');
      await user.click(audioLabel);

      await waitFor(() => {
        expect(screen.getByText(/Upload an audio file/)).toBeInTheDocument();
      });

      // Switch back to text - find the Text label in the radio group
      const textLabels = screen.getAllByText('Text');
      // The first one should be the radio button label
      await user.click(textLabels[0]);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Enter the text you want the digital human to speak/)).toBeInTheDocument();
      });
    });
  });

  describe('Form Validation', () => {
    it('should show validation error for empty text', async () => {
      const user = userEvent.setup();
      render(<GenerateVideoPage />);

      const generateButton = screen.getByRole('button', { name: /generate video/i });
      await user.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter text')).toBeInTheDocument();
      });
    });
  });

  describe('Navigation', () => {
    it('should navigate to detail page when clicking back button', async () => {
      const user = userEvent.setup();
      render(<GenerateVideoPage />);

      const backButton = screen.getByRole('button', { name: /back to detail/i });
      await user.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith('/digital-humans/1');
    });

    it('should navigate to detail page when clicking cancel button', async () => {
      const user = userEvent.setup();
      render(<GenerateVideoPage />);

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      expect(mockNavigate).toHaveBeenCalledWith('/digital-humans/1');
    });
  });

  describe('Video Generation', () => {
    it('should generate video with text input', async () => {
      const user = userEvent.setup();
      const { message } = await import('antd');
      mockGenerateVideo.mockResolvedValue('/videos/generated.mp4');

      render(<GenerateVideoPage />);

      const textInput = screen.getByPlaceholderText(/Enter the text you want the digital human to speak/);
      await user.type(textInput, 'Hello world');

      const generateButton = screen.getByRole('button', { name: /generate video/i });
      await user.click(generateButton);

      await waitFor(() => {
        expect(mockGenerateVideo).toHaveBeenCalled();
        expect(message.success).toHaveBeenCalledWith('Video generated successfully!');
      });
    });

    it('should display generated video after successful generation', async () => {
      const user = userEvent.setup();
      mockGenerateVideo.mockResolvedValue('/videos/generated.mp4');

      render(<GenerateVideoPage />);

      const textInput = screen.getByPlaceholderText(/Enter the text you want the digital human to speak/);
      await user.type(textInput, 'Hello world');

      const generateButton = screen.getByRole('button', { name: /generate video/i });
      await user.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Generated Video')).toBeInTheDocument();
        expect(screen.getByText('/videos/generated.mp4')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message when error occurs', async () => {
      const { message } = await import('antd');
      mockError = 'Failed to fetch digital human';

      render(<GenerateVideoPage />);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith('Failed to fetch digital human');
        expect(mockClearError).toHaveBeenCalled();
      });
    });
  });
});
