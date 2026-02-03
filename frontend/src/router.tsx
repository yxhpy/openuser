import { createBrowserRouter, Navigate } from 'react-router-dom';
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage';
import { DashboardPage } from '@/pages/dashboard/DashboardPage';
import { DigitalHumansListPage } from '@/pages/digitalHuman/ListPage';
import { CreateDigitalHumanPage } from '@/pages/digitalHuman/CreatePage';
import { DigitalHumanDetailPage } from '@/pages/digitalHuman/DetailPage';
import { GenerateVideoPage } from '@/pages/digitalHuman/GenerateVideoPage';
import { PluginsPage } from '@/pages/plugins/PluginsPage';
import { AgentsPage } from '@/pages/agents/AgentsPage';
import { SchedulerPage } from '@/pages/scheduler/SchedulerPage';
import { AppLayout } from '@/components/common/AppLayout';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';
import { ROUTES } from '@/utils/constants';

export const router = createBrowserRouter([
  {
    path: ROUTES.LOGIN,
    element: <LoginPage />,
  },
  {
    path: ROUTES.REGISTER,
    element: <RegisterPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to={ROUTES.DASHBOARD} replace />,
      },
      {
        path: ROUTES.DASHBOARD,
        element: <DashboardPage />,
      },
      {
        path: ROUTES.DIGITAL_HUMANS,
        element: <DigitalHumansListPage />,
      },
      {
        path: '/digital-humans/create',
        element: <CreateDigitalHumanPage />,
      },
      {
        path: '/digital-humans/:id',
        element: <DigitalHumanDetailPage />,
      },
      {
        path: '/digital-humans/:id/generate',
        element: <GenerateVideoPage />,
      },
      {
        path: ROUTES.PLUGINS,
        element: <PluginsPage />,
      },
      {
        path: ROUTES.AGENTS,
        element: <AgentsPage />,
      },
      {
        path: ROUTES.SCHEDULER,
        element: <SchedulerPage />,
      },
    ],
  },
]);
