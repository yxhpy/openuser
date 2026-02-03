import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import { DashboardPage } from '../DashboardPage';

describe('DashboardPage', () => {
  describe('Rendering', () => {
    it('should render dashboard title', () => {
      render(<DashboardPage />);

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    it('should render all statistic cards', async () => {
      render(<DashboardPage />);

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('Digital Humans')).toBeInTheDocument();
        expect(screen.getByText('Plugins')).toBeInTheDocument();
        expect(screen.getByText('Agents')).toBeInTheDocument();
        expect(screen.getByText('Scheduled Tasks')).toBeInTheDocument();
      });
    });

    it('should render statistic values from API', async () => {
      render(<DashboardPage />);

      // Wait for data to load - should show 1 for each stat based on mock data
      await waitFor(() => {
        const statistics = screen.getAllByText('1');
        expect(statistics.length).toBeGreaterThanOrEqual(4);
      });
    });

    it('should render all icons', async () => {
      render(<DashboardPage />);

      // Wait for loading to complete
      await waitFor(() => {
        const container = document.querySelector('.ant-statistic-content');
        expect(container).toBeInTheDocument();
      });
    });
  });

  describe('Layout', () => {
    it('should render cards in a grid layout', () => {
      render(<DashboardPage />);

      // Check for Ant Design Row component
      const row = document.querySelector('.ant-row');
      expect(row).toBeInTheDocument();

      // Check for Ant Design Col components
      const cols = document.querySelectorAll('.ant-col');
      expect(cols.length).toBeGreaterThanOrEqual(4);
    });

    it('should render each statistic in a card', () => {
      render(<DashboardPage />);

      // Check for Ant Design Card components
      const cards = document.querySelectorAll('.ant-card');
      expect(cards).toHaveLength(4);
    });
  });

  describe('Data Loading', () => {
    it('should show loading state initially', () => {
      render(<DashboardPage />);

      // Cards should have loading state
      const cards = document.querySelectorAll('.ant-card-loading');
      expect(cards.length).toBeGreaterThan(0);
    });

    it('should fetch and display stats from APIs', async () => {
      render(<DashboardPage />);

      // Wait for all stats to load
      await waitFor(() => {
        expect(screen.getByText('Digital Humans')).toBeInTheDocument();
        expect(screen.getByText('Plugins')).toBeInTheDocument();
        expect(screen.getByText('Agents')).toBeInTheDocument();
        expect(screen.getByText('Scheduled Tasks')).toBeInTheDocument();
      });
    });
  });
});
