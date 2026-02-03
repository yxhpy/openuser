import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/utils';
import { AgentsPage } from '../AgentsPage';

describe('AgentsPage', () => {
  describe('Rendering', () => {
    it('should render agents title', () => {
      render(<AgentsPage />);

      expect(screen.getByText('Agents')).toBeInTheDocument();
    });

    it('should render placeholder text', () => {
      render(<AgentsPage />);

      expect(
        screen.getByText('Agent management will be displayed here.')
      ).toBeInTheDocument();
    });
  });

  describe('Layout', () => {
    it('should render content in a div container', () => {
      const { container } = render(<AgentsPage />);

      const divs = container.querySelectorAll('div');
      expect(divs.length).toBeGreaterThan(0);
    });

    it('should render title with correct heading level', () => {
      render(<AgentsPage />);

      const heading = screen.getByRole('heading', { level: 2 });
      expect(heading).toHaveTextContent('Agents');
    });
  });
});
