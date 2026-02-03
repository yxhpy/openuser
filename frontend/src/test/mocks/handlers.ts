import { http, HttpResponse } from 'msw';
import type { AuthResponse, User } from '@/types/auth';
import type { DigitalHuman, DigitalHumanListResponse } from '@/types/digitalHuman';
import type { AgentResponse, AgentListResponse } from '@/types/generated';
import type { PluginInfo, PluginListResponse } from '@/api/plugins';
import type { TaskResponse, TaskListResponse } from '@/types/generated';

const API_BASE = 'http://localhost:8000';

// Mock data
const mockUser: User = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  is_active: true,
  is_superuser: false,
  created_at: '2026-02-03T00:00:00Z',
};

const mockAuthResponse: AuthResponse = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'bearer',
  user: mockUser,
};

const mockDigitalHuman: DigitalHuman = {
  id: 1,
  user_id: 1,
  name: 'Test Digital Human',
  description: 'Test description',
  image_path: '/uploads/test.jpg',
  voice_model_path: null,
  video_path: null,
  is_active: true,
  created_at: '2026-02-03T00:00:00Z',
  updated_at: '2026-02-03T00:00:00Z',
};

const mockAgent: AgentResponse = {
  name: 'test-agent',
  system_prompt: 'You are a helpful assistant',
  capabilities: ['plugin-install', 'self-update'],
};

const mockPlugin: PluginInfo = {
  name: 'test-plugin',
  version: '1.0.0',
  dependencies: [],
};

const mockTask: TaskResponse = {
  id: 1,
  user_id: 1,
  name: 'Test Task',
  description: 'Test task description',
  task_type: 'video_generation',
  schedule: '0 0 * * *',
  params: {},
  status: 'pending',
  result: null,
  error_message: null,
  started_at: null,
  completed_at: null,
  created_at: '2026-02-03T00:00:00Z',
  updated_at: '2026-02-03T00:00:00Z',
};

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE}/api/v1/auth/login`, async ({ request }) => {
    const body = await request.json() as { username: string; password: string };

    if (body.username === 'testuser' && body.password === 'Test123!') {
      return HttpResponse.json(mockAuthResponse);
    }

    return HttpResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  http.post(`${API_BASE}/api/v1/auth/register`, async ({ request }) => {
    const body = await request.json() as { username: string; email: string; password: string };

    return HttpResponse.json({
      ...mockAuthResponse,
      user: {
        ...mockUser,
        username: body.username,
        email: body.email,
      },
    });
  }),

  http.post(`${API_BASE}/api/v1/auth/refresh`, async () => {
    return HttpResponse.json({
      access_token: 'new-mock-access-token',
    });
  }),

  http.get(`${API_BASE}/api/v1/auth/me`, () => {
    return HttpResponse.json(mockUser);
  }),

  // Digital Human endpoints
  http.post(`${API_BASE}/api/v1/digital-human/create`, async () => {
    return HttpResponse.json(mockDigitalHuman);
  }),

  http.get(`${API_BASE}/api/v1/digital-human/list`, () => {
    const response: DigitalHumanListResponse = {
      digital_humans: [mockDigitalHuman],
      total: 1,
    };
    return HttpResponse.json(response);
  }),

  http.get(`${API_BASE}/api/v1/digital-human/:id`, ({ params }) => {
    return HttpResponse.json({
      ...mockDigitalHuman,
      id: Number(params.id),
    });
  }),

  http.delete(`${API_BASE}/api/v1/digital-human/:id`, () => {
    return HttpResponse.json({ message: 'Deleted successfully' });
  }),

  http.post(`${API_BASE}/api/v1/digital-human/generate`, async () => {
    return HttpResponse.json({
      video_path: '/uploads/generated-video.mp4',
      digital_human_id: 1,
      mode: 'enhanced_talking_head',
      message: 'Video generated successfully',
    });
  }),

  // Agent endpoints
  http.get(`${API_BASE}/api/v1/agents/list`, () => {
    const response: AgentListResponse = {
      agents: [mockAgent],
      total: 1,
    };
    return HttpResponse.json(response);
  }),

  http.post(`${API_BASE}/api/v1/agents/create`, async ({ request }) => {
    const body = await request.json() as AgentResponse;
    return HttpResponse.json({
      ...mockAgent,
      ...body,
    });
  }),

  http.get(`${API_BASE}/api/v1/agents/:name`, ({ params }) => {
    return HttpResponse.json({
      ...mockAgent,
      name: params.name as string,
    });
  }),

  http.put(`${API_BASE}/api/v1/agents/:name`, async ({ request, params }) => {
    const body = await request.json() as Partial<AgentResponse>;
    return HttpResponse.json({
      ...mockAgent,
      name: params.name as string,
      ...body,
    });
  }),

  http.delete(`${API_BASE}/api/v1/agents/:name`, () => {
    return HttpResponse.json({ message: 'Agent deleted successfully' });
  }),

  // Plugin endpoints
  http.get(`${API_BASE}/api/v1/plugins/list`, () => {
    const response: PluginListResponse = {
      plugins: [mockPlugin],
      total: 1,
    };
    return HttpResponse.json(response);
  }),

  http.post(`${API_BASE}/api/v1/plugins/install`, async ({ request }) => {
    const body = await request.json() as { name: string };
    return HttpResponse.json({
      name: body.name,
      version: '1.0.0',
      message: 'Plugin installed successfully',
    });
  }),

  http.post(`${API_BASE}/api/v1/plugins/reload`, async ({ request }) => {
    const body = await request.json() as { name: string };
    return HttpResponse.json({
      name: body.name,
      version: '1.0.0',
      message: 'Plugin reloaded successfully',
    });
  }),

  // Scheduler endpoints
  http.get(`${API_BASE}/api/v1/scheduler/list`, () => {
    const response: TaskListResponse = {
      tasks: [mockTask],
      total: 1,
    };
    return HttpResponse.json(response);
  }),

  http.post(`${API_BASE}/api/v1/scheduler/create`, async ({ request }) => {
    const body = await request.json() as Partial<TaskResponse>;
    return HttpResponse.json({
      ...mockTask,
      ...body,
      id: 2,
    });
  }),

  http.get(`${API_BASE}/api/v1/scheduler/:taskId`, ({ params }) => {
    return HttpResponse.json({
      ...mockTask,
      id: Number(params.taskId),
    });
  }),

  http.put(`${API_BASE}/api/v1/scheduler/:taskId`, async ({ request, params }) => {
    const body = await request.json() as Partial<TaskResponse>;
    return HttpResponse.json({
      ...mockTask,
      id: Number(params.taskId),
      ...body,
    });
  }),

  http.delete(`${API_BASE}/api/v1/scheduler/:taskId`, () => {
    return HttpResponse.json({ message: 'Task deleted successfully' });
  }),
];
