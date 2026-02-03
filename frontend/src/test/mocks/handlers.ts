import { http, HttpResponse } from 'msw';
import type { AuthResponse, User } from '@/types/auth';
import type { DigitalHuman, DigitalHumanListResponse } from '@/types/digitalHuman';

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
];
