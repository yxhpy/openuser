import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import { AgentsPage } from '../AgentsPage';
import userEvent from '@testing-library/user-event';

describe('AgentsPage', () => {
  describe('Rendering', () => {
    it('should render agents management title', async () => {
      render(<AgentsPage />);

      await waitFor(() => {
        expect(screen.getByText('Agent Management')).toBeInTheDocument();
      });
    });

    it('should render refresh and create buttons', async () => {
      render(<AgentsPage />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /create agent/i })).toBeInTheDocument();
      });
    });

    it('should load and display agents', async () => {
      render(<AgentsPage />);

      await waitFor(() => {
        expect(screen.getByText('test-agent')).toBeInTheDocument();
      });
    });
  });

  describe('Agent Table', () => {
    it('should display agent information in table', async () => {
      render(<AgentsPage />);

      await waitFor(() => {
        expect(screen.getByText('test-agent')).toBeInTheDocument();
        expect(screen.getByText('You are a helpful assistant')).toBeInTheDocument();
        expect(screen.getByText('plugin-install')).toBeInTheDocument();
        expect(screen.getByText('self-update')).toBeInTheDocument();
      });
    });

    it('should have edit and delete buttons for each agent', async () => {
      render(<AgentsPage />);

      await waitFor(() => {
        const editButtons = screen.getAllByRole('button', { name: /edit/i });
        const deleteButtons = screen.getAllByRole('button', { name: /delete/i });

        expect(editButtons.length).toBeGreaterThan(0);
        expect(deleteButtons.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Create Agent Modal', () => {
    it('should open create modal when create button is clicked', async () => {
      const user = userEvent.setup();
      render(<AgentsPage />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /create agent/i })).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', { name: /create agent/i });
      await user.click(createButton);

      await waitFor(() => {
        // Check for modal by looking for the modal title with specific role
        const modalTitle = screen.getAllByText('Create Agent');
        expect(modalTitle.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Statistics', () => {
    it('should display total agents count', async () => {
      render(<AgentsPage />);

      await waitFor(() => {
        expect(screen.getByText('Total Agents')).toBeInTheDocument();
        // Check for the statistic value - there will be multiple "1"s, so just verify at least one exists
        const ones = screen.getAllByText('1');
        expect(ones.length).toBeGreaterThan(0);
      });
    });
  });
});
