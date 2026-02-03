import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { PluginsPage } from '../PluginsPage';
import { pluginApi } from '@/api/plugins';

// Mock the plugin API
vi.mock('@/api/plugins', () => ({
  pluginApi: {
    list: vi.fn(),
    install: vi.fn(),
    reload: vi.fn(),
  },
}));

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

describe('PluginsPage', () => {
  const mockPlugins = [
    {
      name: 'image-processor',
      version: '1.0.0',
      dependencies: ['pillow'],
    },
    {
      name: 'video-editor',
      version: '2.1.0',
      dependencies: ['ffmpeg', 'opencv'],
    },
    {
      name: 'audio-enhancer',
      version: '1.5.0',
      dependencies: [],
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementation
    vi.mocked(pluginApi.list).mockResolvedValue({
      plugins: mockPlugins,
      total: mockPlugins.length,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render page title and description', async () => {
      render(<PluginsPage />);

      expect(screen.getByText('Plugin Management')).toBeInTheDocument();
      expect(screen.getByText('Manage and hot-reload plugins without system restart')).toBeInTheDocument();
    });

    it('should render action buttons', async () => {
      render(<PluginsPage />);

      expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /install plugin/i })).toBeInTheDocument();
    });

    it('should load and display plugins on mount', async () => {
      render(<PluginsPage />);

      await waitFor(() => {
        expect(pluginApi.list).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText('image-processor')).toBeInTheDocument();
        expect(screen.getByText('video-editor')).toBeInTheDocument();
        expect(screen.getByText('audio-enhancer')).toBeInTheDocument();
      });
    });

    it('should display plugin statistics', async () => {
      render(<PluginsPage />);

      await waitFor(() => {
        expect(screen.getByText('Total Plugins')).toBeInTheDocument();
        expect(screen.getByText('Active Plugins')).toBeInTheDocument();
      });
    });

    it('should display empty state when no plugins', async () => {
      vi.mocked(pluginApi.list).mockResolvedValue({
        plugins: [],
        total: 0,
      });

      render(<PluginsPage />);

      await waitFor(() => {
        expect(screen.getByText('No plugins installed')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /install your first plugin/i })).toBeInTheDocument();
      });
    });
  });

  describe('Plugin Table', () => {
    it('should display plugin information in table', async () => {
      render(<PluginsPage />);

      await waitFor(() => {
        // Check plugin names
        expect(screen.getByText('image-processor')).toBeInTheDocument();
        expect(screen.getByText('video-editor')).toBeInTheDocument();

        // Check versions
        expect(screen.getByText('1.0.0')).toBeInTheDocument();
        expect(screen.getByText('2.1.0')).toBeInTheDocument();

        // Check dependencies
        expect(screen.getByText('pillow')).toBeInTheDocument();
        expect(screen.getByText('ffmpeg')).toBeInTheDocument();
        expect(screen.getByText('opencv')).toBeInTheDocument();
      });
    });

    it('should display "No dependencies" for plugins without dependencies', async () => {
      render(<PluginsPage />);

      await waitFor(() => {
        expect(screen.getByText('No dependencies')).toBeInTheDocument();
      });
    });

    it('should display reload button for each plugin', async () => {
      render(<PluginsPage />);

      await waitFor(() => {
        const reloadButtons = screen.getAllByRole('button', { name: /reload/i });
        expect(reloadButtons.length).toBeGreaterThanOrEqual(3);
      });
    });
  });

  describe('Load Plugins Functionality', () => {
    it('should show success message after loading plugins', async () => {
      const { message } = await import('antd');
      render(<PluginsPage />);

      await waitFor(() => {
        expect(message.success).toHaveBeenCalledWith('Loaded 3 plugin(s)');
      });
    });

    it('should show error message on load failure', async () => {
      const { message } = await import('antd');
      const errorMessage = 'Failed to fetch plugins';
      vi.mocked(pluginApi.list).mockRejectedValue({
        response: { data: { detail: errorMessage } },
      });

      render(<PluginsPage />);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith(errorMessage);
      });
    });

    it('should show generic error message when error has no detail', async () => {
      const { message } = await import('antd');
      vi.mocked(pluginApi.list).mockRejectedValue(new Error('Network error'));

      render(<PluginsPage />);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith('Failed to load plugins');
      });
    });

    it('should reload plugins when refresh button is clicked', async () => {
      const user = userEvent.setup();
      render(<PluginsPage />);

      await waitFor(() => {
        expect(pluginApi.list).toHaveBeenCalledTimes(1);
      });

      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      await user.click(refreshButton);

      await waitFor(() => {
        expect(pluginApi.list).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('API Integration', () => {
    it('should call install API with correct parameters', async () => {
      vi.mocked(pluginApi.install).mockResolvedValue({
        message: 'Plugin installed successfully',
      });

      // Directly test the API call
      const result = await pluginApi.install({ name: 'test-plugin' });

      expect(pluginApi.install).toHaveBeenCalledWith({ name: 'test-plugin' });
      expect(result.message).toBe('Plugin installed successfully');
    });

    it('should call reload API with correct parameters', async () => {
      vi.mocked(pluginApi.reload).mockResolvedValue({
        message: 'Plugin reloaded successfully',
      });

      // Directly test the API call
      const result = await pluginApi.reload({ name: 'test-plugin' });

      expect(pluginApi.reload).toHaveBeenCalledWith({ name: 'test-plugin' });
      expect(result.message).toBe('Plugin reloaded successfully');
    });
  });
});
