import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { server } from '@/test/mocks/server';
import { http, HttpResponse } from 'msw';
import { authApi } from '@/api/auth';
import * as digitalHumanAPI from '@/api/digitalHuman';
import { pluginApi } from '@/api/plugins';

const API_BASE = 'http://localhost:8000';

/**
 * API Integration Tests
 * Tests the integration between frontend API clients and backend endpoints
 * using MSW (Mock Service Worker) to simulate backend responses
 */
describe('API Integration Tests', () => {
  beforeEach(() => {
    // Clear any stored tokens
    localStorage.clear();
  });

  afterEach(() => {
    server.resetHandlers();
  });

  describe('Authentication API Integration', () => {
    it('should successfully login and store token', async () => {
      // Mock successful login response
      server.use(
        http.post(`${API_BASE}/api/v1/auth/login`, () => {
          return HttpResponse.json({
            access_token: 'mock-jwt-token',
            token_type: 'bearer',
          });
        })
      );

      const result = await authApi.login({
        username: 'testuser',
        password: 'Password123!',
      });

      expect(result.access_token).toBe('mock-jwt-token');
      expect(result.token_type).toBe('bearer');
    });

    it('should handle login failure', async () => {
      // Mock failed login response
      server.use(
        http.post(`${API_BASE}/api/v1/auth/login`, () => {
          return HttpResponse.json(
            { detail: 'Invalid credentials' },
            { status: 401 }
          );
        })
      );

      await expect(
        authApi.login({
          username: 'wronguser',
          password: 'wrongpassword',
        })
      ).rejects.toThrow();
    });

    it('should successfully register a new user', async () => {
      // Mock successful registration response
      server.use(
        http.post(`${API_BASE}/api/v1/auth/register`, () => {
          return HttpResponse.json({
            access_token: 'mock-jwt-token',
            refresh_token: 'mock-refresh-token',
            token_type: 'bearer',
            expires_in: 3600,
            user: {
              id: 1,
              username: 'newuser',
              email: 'new@example.com',
              is_active: true,
              is_superuser: false,
              created_at: new Date().toISOString(),
            },
          });
        })
      );

      const result = await authApi.register({
        username: 'newuser',
        email: 'new@example.com',
        password: 'Password123!',
      });

      expect(result.user.username).toBe('newuser');
      expect(result.user.email).toBe('new@example.com');
      expect(result.access_token).toBe('mock-jwt-token');
    });

    it('should handle registration with existing username', async () => {
      // Mock registration failure
      server.use(
        http.post(`${API_BASE}/api/v1/auth/register`, () => {
          return HttpResponse.json(
            { detail: 'Username already exists' },
            { status: 400 }
          );
        })
      );

      await expect(
        authApi.register({
          username: 'existinguser',
          email: 'test@example.com',
          password: 'Password123!',
        })
      ).rejects.toThrow();
    });
  });

  describe('Digital Human API Integration', () => {
    beforeEach(() => {
      // Set auth token for authenticated requests
      localStorage.setItem('token', 'mock-jwt-token');
    });

    it('should fetch list of digital humans', async () => {
      // Mock digital humans list response
      server.use(
        http.get(`${API_BASE}/api/v1/digital-human/list`, () => {
          return HttpResponse.json({
            digital_humans: [
              {
                id: 1,
                user_id: 1,
                name: 'Test Human 1',
                description: 'A test digital human',
                image_path: '/images/test1.jpg',
                is_active: true,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
              },
              {
                id: 2,
                user_id: 1,
                name: 'Test Human 2',
                description: 'Another test digital human',
                image_path: '/images/test2.jpg',
                is_active: true,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
              },
            ],
            total: 2,
          });
        })
      );

      const result = await digitalHumanAPI.listDigitalHumans();

      expect(result.digital_humans).toHaveLength(2);
      expect(result.total).toBe(2);
      expect(result.digital_humans[0].name).toBe('Test Human 1');
    });

    it('should create a new digital human', async () => {
      // Mock create digital human response
      server.use(
        http.post(`${API_BASE}/api/v1/digital-human/create`, () => {
          return HttpResponse.json({
            id: 3,
            user_id: 1,
            name: 'New Digital Human',
            description: 'A newly created digital human',
            image_path: '/images/new.jpg',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        })
      );

      const result = await digitalHumanAPI.createDigitalHuman({
        name: 'New Digital Human',
        description: 'A newly created digital human',
      });

      expect(result.id).toBe(3);
      expect(result.name).toBe('New Digital Human');
    });

    it('should get digital human details', async () => {
      // Mock get digital human details response
      server.use(
        http.get(`${API_BASE}/api/v1/digital-human/:id`, ({ params }) => {
          return HttpResponse.json({
            id: Number(params.id),
            user_id: 1,
            name: 'Test Digital Human',
            description: 'A test digital human',
            image_path: '/images/test.jpg',
            voice_model_path: 'voice-123',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        })
      );

      const result = await digitalHumanAPI.getDigitalHuman(1);

      expect(result.id).toBe(1);
      expect(result.name).toBe('Test Digital Human');
      expect(result.voice_model_path).toBe('voice-123');
    });

    it('should delete a digital human', async () => {
      // Mock delete digital human response
      server.use(
        http.delete(`${API_BASE}/api/v1/digital-human/:id`, () => {
          return HttpResponse.json({ message: 'Digital human deleted successfully' });
        })
      );

      await expect(digitalHumanAPI.deleteDigitalHuman(1)).resolves.not.toThrow();
    });

    it('should generate video for digital human', async () => {
      // Mock generate video response
      server.use(
        http.post(`${API_BASE}/api/v1/digital-human/generate`, () => {
          return HttpResponse.json({
            video_path: '/videos/generated-123.mp4',
            digital_human_id: 1,
            mode: 'lipsync',
            message: 'Video generation started',
          });
        })
      );

      const result = await digitalHumanAPI.generateVideo({
        digital_human_id: 1,
        text: 'Hello, this is a test video',
        mode: 'lipsync',
      });

      expect(result.video_path).toBe('/videos/generated-123.mp4');
      expect(result.digital_human_id).toBe(1);
    });
  });

  describe('Plugins API Integration', () => {
    beforeEach(() => {
      // Set auth token for authenticated requests
      localStorage.setItem('token', 'mock-jwt-token');
    });

    it('should fetch list of plugins', async () => {
      // Mock plugins list response
      server.use(
        http.get(`${API_BASE}/api/v1/plugins/list`, () => {
          return HttpResponse.json({
            plugins: [
              {
                name: 'image-processor',
                version: '1.0.0',
                description: 'Image preprocessing plugin',
                status: 'active',
                installed_at: new Date().toISOString(),
              },
              {
                name: 'video-editor',
                version: '1.2.0',
                description: 'Video editing utilities',
                status: 'active',
                installed_at: new Date().toISOString(),
              },
            ],
          });
        })
      );

      const result = await pluginApi.list();

      expect(result.plugins).toHaveLength(2);
      expect(result.plugins[0].name).toBe('image-processor');
      expect(result.plugins[1].name).toBe('video-editor');
    });

    it('should install a new plugin', async () => {
      // Mock install plugin response
      server.use(
        http.post(`${API_BASE}/api/v1/plugins/install`, () => {
          return HttpResponse.json({
            name: 'new-plugin',
            version: '1.0.0',
            status: 'active',
            message: 'Plugin installed successfully',
          });
        })
      );

      const result = await pluginApi.install({
        name: 'new-plugin',
      });

      expect(result.name).toBe('new-plugin');
      expect(result.status).toBe('active');
    });

    it('should reload a plugin', async () => {
      // Mock reload plugin response
      server.use(
        http.post(`${API_BASE}/api/v1/plugins/reload`, () => {
          return HttpResponse.json({
            name: 'image-processor',
            status: 'active',
            message: 'Plugin reloaded successfully',
          });
        })
      );

      const result = await pluginApi.reload({ name: 'image-processor' });

      expect(result.name).toBe('image-processor');
      expect(result.status).toBe('active');
    });

    it('should handle plugin installation failure', async () => {
      // Mock plugin installation failure
      server.use(
        http.post(`${API_BASE}/api/v1/plugins/install`, () => {
          return HttpResponse.json(
            { detail: 'Plugin not found in registry' },
            { status: 404 }
          );
        })
      );

      await expect(
        pluginApi.install({
          name: 'non-existent-plugin',
        })
      ).rejects.toThrow();
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle network errors', async () => {
      // Mock network error
      server.use(
        http.get(`${API_BASE}/api/v1/digital-human/list`, () => {
          return HttpResponse.error();
        })
      );

      await expect(digitalHumanAPI.listDigitalHumans()).rejects.toThrow();
    });

    it('should handle 500 server errors', async () => {
      // Mock server error
      server.use(
        http.get(`${API_BASE}/api/v1/digital-human/list`, () => {
          return HttpResponse.json(
            { detail: 'Internal server error' },
            { status: 500 }
          );
        })
      );

      await expect(digitalHumanAPI.listDigitalHumans()).rejects.toThrow();
    });

    it.skip('should handle unauthorized requests', async () => {
      // Clear token and refresh token
      localStorage.clear();

      // Mock unauthorized response
      server.use(
        http.get(`${API_BASE}/api/v1/digital-human/list`, () => {
          return HttpResponse.json(
            { detail: 'Not authenticated' },
            { status: 401 }
          );
        }),
        // Mock refresh endpoint to also fail
        http.post(`${API_BASE}/api/v1/auth/refresh`, () => {
          return HttpResponse.json(
            { detail: 'Invalid refresh token' },
            { status: 401 }
          );
        })
      );

      await expect(digitalHumanAPI.listDigitalHumans()).rejects.toThrow();
    });
  });
});
