import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/utils';
import { DashboardPage } from '../DashboardPage';

describe('DashboardPage', () => {
  describe('Rendering', () => {
    it('should render dashboard title', () => {
      render(<DashboardPage />);

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    it('should render all statistic cards', () => {
      render(<DashboardPage />);

      // Check all statistic titles
      expect(screen.getByText('Digital Humans')).toBeInTheDocument();
      expect(screen.getByText('Plugins')).toBeInTheDocument();
      expect(screen.getByText('Agents')).toBeInTheDocument();
      expect(screen.getByText('Scheduled Tasks')).toBeInTheDocument();
    });

    it('should render all statistic values as 0', () => {
      render(<DashboardPage />);

      // Get all elements with value 0
      const statistics = screen.getAllByText('0');
      expect(statistics).toHaveLength(4);
    });

    it('should render all icons', () => {
      render(<DashboardPage />);

      // Check for icon containers (Ant Design renders icons as spans with specific classes)
      const container = document.querySelector('.ant-statistic-content');
      expect(container).toBeInTheDocument();
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
});
