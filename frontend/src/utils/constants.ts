export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const TOKEN_KEY = 'openuser_access_token';
export const REFRESH_TOKEN_KEY = 'openuser_refresh_token';
export const USER_KEY = 'openuser_user';

export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  DIGITAL_HUMANS: '/digital-humans',
  DIGITAL_HUMANS_CREATE: '/digital-humans/create',
  DIGITAL_HUMANS_DETAIL: '/digital-humans/:id',
  DIGITAL_HUMANS_GENERATE: '/digital-humans/:id/generate',
  PLUGINS: '/plugins',
  AGENTS: '/agents',
  SCHEDULER: '/scheduler',
} as const;
