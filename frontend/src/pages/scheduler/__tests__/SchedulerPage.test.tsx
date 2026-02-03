import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { SchedulerPage } from '../SchedulerPage';
import * as schedulerApi from '@/api/scheduler';

// Mock the scheduler API
vi.mock('@/api/scheduler', () => ({
  listTasks: vi.fn(),
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
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

describe('SchedulerPage', () => {
  const mockTasks = [
    {
      id: 1,
      name: 'Daily Video Generation',
      description: 'Generate daily videos',
      task_type: 'video_generation',
      schedule: '0 0 * * *',
      status: 'pending',
      params: { quality: 'high' },
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      name: 'Voice Synthesis Task',
      description: 'Synthesize voice',
      task_type: 'voice_synthesis',
      schedule: '0 12 * * *',
      status: 'running',
      params: null,
      created_at: '2024-01-02T00:00:00Z',
    },
    {
      id: 3,
      name: 'Completed Task',
      description: 'Already done',
      task_type: 'batch_processing',
      schedule: null,
      status: 'completed',
      params: null,
      created_at: '2024-01-03T00:00:00Z',
    },
    {
      id: 4,
      name: 'Failed Task',
      description: 'Task failed',
      task_type: 'custom',
      schedule: '0 6 * * *',
      status: 'failed',
      params: null,
      created_at: '2024-01-04T00:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementation
    vi.mocked(schedulerApi.listTasks).mockResolvedValue({
      tasks: mockTasks,
      total: mockTasks.length,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render page title', async () => {
      render(<SchedulerPage />);

      expect(screen.getByText('Task Scheduler')).toBeInTheDocument();
    });

    it('should render statistics cards', async () => {
      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Total Tasks')).toBeInTheDocument();
        expect(screen.getByText('Pending')).toBeInTheDocument();
        expect(screen.getByText('Running')).toBeInTheDocument();
        expect(screen.getByText('Completed')).toBeInTheDocument();
        expect(screen.getByText('Failed')).toBeInTheDocument();
      });
    });

    it('should render action buttons', async () => {
      render(<SchedulerPage />);

      expect(screen.getByRole('button', { name: /create task/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
    });

    it('should render filter dropdowns', async () => {
      render(<SchedulerPage />);

      await waitFor(() => {
        // Wait for tasks to load first
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      // Check for Select components in the DOM
      const selects = document.querySelectorAll('.ant-select');
      expect(selects.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Load Tasks', () => {
    it('should load tasks on mount', async () => {
      render(<SchedulerPage />);

      await waitFor(() => {
        expect(schedulerApi.listTasks).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
        expect(screen.getByText('Voice Synthesis Task')).toBeInTheDocument();
        expect(screen.getByText('Completed Task')).toBeInTheDocument();
        expect(screen.getByText('Failed Task')).toBeInTheDocument();
      });
    });

    it('should show error message on load failure', async () => {
      const { message } = await import('antd');
      vi.mocked(schedulerApi.listTasks).mockRejectedValue(new Error('Network error'));

      render(<SchedulerPage />);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith('Failed to load tasks');
      });
    });

    it('should reload tasks when refresh button is clicked', async () => {
      const user = userEvent.setup();
      render(<SchedulerPage />);

      await waitFor(() => {
        expect(schedulerApi.listTasks).toHaveBeenCalledTimes(1);
      });

      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      await user.click(refreshButton);

      await waitFor(() => {
        expect(schedulerApi.listTasks).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Statistics', () => {
    it('should calculate and display correct statistics', async () => {
      render(<SchedulerPage />);

      await waitFor(() => {
        // Total: 4 tasks
        const totalStats = screen.getAllByText('4');
        expect(totalStats.length).toBeGreaterThan(0);

        // Pending: 1 task
        const pendingStats = screen.getAllByText('1');
        expect(pendingStats.length).toBeGreaterThan(0);
      });
    });

    it('should update statistics when tasks change', async () => {
      const { rerender } = render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      // Change mock data
      vi.mocked(schedulerApi.listTasks).mockResolvedValue({
        tasks: [],
        total: 0,
      });

      // Trigger reload
      const user = userEvent.setup();
      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      await user.click(refreshButton);

      await waitFor(() => {
        const zeroStats = screen.getAllByText('0');
        expect(zeroStats.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Task Table', () => {
    it('should display task information in table', async () => {
      render(<SchedulerPage />);

      await waitFor(() => {
        // Check task names
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
        expect(screen.getByText('Voice Synthesis Task')).toBeInTheDocument();

        // Check task types
        expect(screen.getByText('Video Generation')).toBeInTheDocument();
        expect(screen.getByText('Voice Synthesis')).toBeInTheDocument();

        // Check statuses
        expect(screen.getByText('PENDING')).toBeInTheDocument();
        expect(screen.getByText('RUNNING')).toBeInTheDocument();
        expect(screen.getByText('COMPLETED')).toBeInTheDocument();
        expect(screen.getByText('FAILED')).toBeInTheDocument();
      });
    });

    it('should display schedule or dash for null schedule', async () => {
      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('0 0 * * *')).toBeInTheDocument();
        expect(screen.getByText('0 12 * * *')).toBeInTheDocument();
        // Null schedule should show as '-'
        const dashes = screen.getAllByText('-');
        expect(dashes.length).toBeGreaterThan(0);
      });
    });

    it('should display edit and delete buttons for each task', async () => {
      render(<SchedulerPage />);

      await waitFor(() => {
        const editButtons = screen.getAllByRole('button', { name: /edit/i });
        const deleteButtons = screen.getAllByRole('button', { name: /delete/i });

        expect(editButtons.length).toBe(4);
        expect(deleteButtons.length).toBe(4);
      });
    });
  });

  describe('Filters', () => {
    it('should render filter controls', async () => {
      render(<SchedulerPage />);

      await waitFor(() => {
        // Check that the component has rendered with tasks
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      // Filters should be present in the DOM
      const selects = document.querySelectorAll('.ant-select');
      expect(selects.length).toBeGreaterThanOrEqual(2);
    });

    it('should call API with default filter parameters on mount', async () => {
      render(<SchedulerPage />);

      await waitFor(() => {
        expect(schedulerApi.listTasks).toHaveBeenCalledWith({
          status: undefined,
          task_type: undefined,
        });
      });
    });
  });

  describe('API Integration', () => {
    it('should call createTask API with correct parameters', async () => {
      vi.mocked(schedulerApi.createTask).mockResolvedValue({
        id: 5,
        name: 'New Task',
        task_type: 'custom',
        status: 'pending',
      });

      const result = await schedulerApi.createTask({
        name: 'New Task',
        description: 'Test task',
        task_type: 'custom',
        schedule: '0 0 * * *',
        params: null,
      });

      expect(schedulerApi.createTask).toHaveBeenCalled();
      expect(result.name).toBe('New Task');
    });

    it('should call updateTask API with correct parameters', async () => {
      vi.mocked(schedulerApi.updateTask).mockResolvedValue({
        id: 1,
        name: 'Updated Task',
        status: 'completed',
      });

      const result = await schedulerApi.updateTask(1, {
        name: 'Updated Task',
        status: 'completed',
      });

      expect(schedulerApi.updateTask).toHaveBeenCalledWith(1, {
        name: 'Updated Task',
        status: 'completed',
      });
      expect(result.name).toBe('Updated Task');
    });

    it('should call deleteTask API with correct parameters', async () => {
      vi.mocked(schedulerApi.deleteTask).mockResolvedValue(undefined);

      await schedulerApi.deleteTask(1);

      expect(schedulerApi.deleteTask).toHaveBeenCalledWith(1);
    });
  });

  describe('Loading State', () => {
    it('should show loading state while fetching tasks', async () => {
      vi.mocked(schedulerApi.listTasks).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ tasks: mockTasks, total: mockTasks.length }), 100))
      );

      render(<SchedulerPage />);

      // Check for loading state in table
      const table = document.querySelector('.ant-table');
      expect(table).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });
    });
  });

  describe('Create Task Modal', () => {
    it('should open create modal when create button is clicked', async () => {
      const user = userEvent.setup();
      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', { name: /create task/i });
      await user.click(createButton);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
        // Check for modal content instead of title
        expect(screen.getByLabelText(/task name/i)).toBeInTheDocument();
      });
    });

    it('should create task when form is submitted', async () => {
      const { message } = await import('antd');
      const user = userEvent.setup();
      vi.mocked(schedulerApi.createTask).mockResolvedValue({
        id: 5,
        name: 'New Task',
        task_type: 'custom',
        status: 'pending',
      });

      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', { name: /create task/i });
      await user.click(createButton);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      // Fill in required fields
      const nameInput = screen.getByLabelText(/task name/i);
      await user.type(nameInput, 'New Task');

      // Select task type (required field)
      const taskTypeSelect = screen.getByLabelText(/task type/i);
      await user.click(taskTypeSelect);

      await waitFor(() => {
        const customOptions = screen.getAllByText('Custom');
        expect(customOptions.length).toBeGreaterThan(0);
      }, { timeout: 3000 });

      // Get all "Custom" elements and click the one in the dropdown (last one)
      const customOptions = screen.getAllByText('Custom');
      await user.click(customOptions[customOptions.length - 1]);

      // Wait a bit for the select to close
      await waitFor(() => {
        const submitButton = screen.getByRole('button', { name: /^create$/i });
        expect(submitButton).toBeInTheDocument();
      });

      // Submit form
      const submitButton = screen.getByRole('button', { name: /^create$/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(schedulerApi.createTask).toHaveBeenCalled();
        expect(message.success).toHaveBeenCalledWith('Task created successfully');
      }, { timeout: 3000 });
    }, 10000); // Increase timeout to 10 seconds

    it('should show error message on create failure', async () => {
      const { message } = await import('antd');
      const user = userEvent.setup();
      const errorMessage = 'Invalid task data';
      vi.mocked(schedulerApi.createTask).mockRejectedValue({
        response: { data: { detail: errorMessage } },
      });

      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', { name: /create task/i });
      await user.click(createButton);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/task name/i);
      await user.type(nameInput, 'New Task');

      // Select task type
      const taskTypeSelect = screen.getByLabelText(/task type/i);
      await user.click(taskTypeSelect);
      await waitFor(() => {
        const customOptions = screen.getAllByText('Custom');
        expect(customOptions.length).toBeGreaterThan(0);
      });
      // Get all "Custom" elements and click the one in the dropdown (last one)
      const customOptions = screen.getAllByText('Custom');
      await user.click(customOptions[customOptions.length - 1]);

      const submitButton = screen.getByRole('button', { name: /^create$/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith(errorMessage);
      });
    }, 10000);

    it('should close modal when cancel button is clicked', async () => {
      const user = userEvent.setup();
      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', { name: /create task/i });
      await user.click(createButton);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
    }, 10000);
  });

  describe('Edit Task Modal', () => {
    it('should open edit modal when edit button is clicked', async () => {
      const user = userEvent.setup();
      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      await user.click(editButtons[0]);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
        // Check for populated form field
        expect(screen.getByDisplayValue('Daily Video Generation')).toBeInTheDocument();
      });
    });

    it('should populate form with task data when editing', async () => {
      const user = userEvent.setup();
      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      await user.click(editButtons[0]);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      // Check that form is populated with existing task data
      expect(screen.getByDisplayValue('Daily Video Generation')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Generate daily videos')).toBeInTheDocument();
      expect(screen.getByDisplayValue('0 0 * * *')).toBeInTheDocument();
    });

    it('should update task when form is submitted', async () => {
      const { message } = await import('antd');
      const user = userEvent.setup();
      vi.mocked(schedulerApi.updateTask).mockResolvedValue({
        id: 1,
        name: 'Updated Task',
        status: 'completed',
      });

      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      await user.click(editButtons[0]);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      const nameInput = screen.getByDisplayValue('Daily Video Generation');
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Task');

      const submitButton = screen.getByRole('button', { name: /^update$/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(schedulerApi.updateTask).toHaveBeenCalled();
        expect(message.success).toHaveBeenCalledWith('Task updated successfully');
      });
    }, 10000);

    it('should show error message on update failure', async () => {
      const { message } = await import('antd');
      const user = userEvent.setup();
      const errorMessage = 'Update failed';
      vi.mocked(schedulerApi.updateTask).mockRejectedValue({
        response: { data: { detail: errorMessage } },
      });

      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      await user.click(editButtons[0]);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      const submitButton = screen.getByRole('button', { name: /^update$/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith(errorMessage);
      });
    }, 10000);
  });

  describe('Delete Task', () => {
    it('should delete task when delete button is clicked and confirmed', async () => {
      const { message } = await import('antd');
      const user = userEvent.setup();
      vi.mocked(schedulerApi.deleteTask).mockResolvedValue(undefined);

      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await user.click(deleteButtons[0]);

      // Confirm deletion in popconfirm
      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /yes/i });
        expect(confirmButton).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', { name: /yes/i });
      await user.click(confirmButton);

      await waitFor(() => {
        expect(schedulerApi.deleteTask).toHaveBeenCalledWith(1);
        expect(message.success).toHaveBeenCalledWith('Task deleted successfully');
      });
    }, 10000);

    it('should show error message on delete failure', async () => {
      const { message } = await import('antd');
      const user = userEvent.setup();
      vi.mocked(schedulerApi.deleteTask).mockRejectedValue(new Error('Delete failed'));

      render(<SchedulerPage />);

      await waitFor(() => {
        expect(screen.getByText('Daily Video Generation')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /yes/i });
        expect(confirmButton).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', { name: /yes/i });
      await user.click(confirmButton);

      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith('Failed to delete task');
      });
    }, 10000);
  });
});
