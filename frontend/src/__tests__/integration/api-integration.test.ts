import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { server } from '@/test/mocks/server';
import { http, HttpResponse } from 'msw';
import * as authAPI from '@/api/auth';
import * as digitalHumanAPI from '@/api/digitalHuman';
import * as pluginsAPI from '@/api/plugins';

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
        http.post('/api/v1/auth/login', () => {
          return HttpResponse.json({
            access_token: 'mock-jwt-token',
            token_type: 'bearer',
          });
        })
      );

      const result = await authAPI.login({
        username: 'testuser',
        password: 'Password123!',
      });

      expect(result.access_token).toBe('mock-jwt-token');
      expect(result.token_type).toBe('bearer');
    });

    it('should handle login failure', async () => {
      // Mock failed login response
      server.use(
        http.post('/api/v1/auth/login', () => {
          return HttpResponse.json(
            { detail: 'Invalid credentials' },
            { status: 401 }
          );
        })
      );

      await expect(
        authAPI.login({
          username: 'wronguser',
          password: 'wrongpassword',
        })
      ).rejects.toThrow();
    });

    it('should successfully register a new user', async () => {
      // Mock successful registration response
      server.use(
        http.post('/api/v1/auth/register', () => {
          return HttpResponse.json({
            id: 1,
            username: 'newuser',
            email: 'new@example.com',
            created_at: new Date().toISOString(),
          });
        })
      );

      const result = await authAPI.register({
        username: 'newuser',
        email: 'new@example.com',
        password: 'Password123!',
      });

      expect(result.username).toBe('newuser');
      expect(result.email).toBe('new@example.com');
    });

    it('should handle registration with existing username', async () => {
      // Mock registration failure
      server.use(
        http.post('/api/v1/auth/register', () => {
          return HttpResponse.json(
            { detail: 'Username already exists' },
            { status: 400 }
          );
        })
      );

      await expect(
        authAPI.register({
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
        http.get('/api/v1/digital-human/list', () => {
          return HttpResponse.json({
            items: [
              {
                id: 1,
                name: 'Test Human 1',
                description: 'A test digital human',
                image_url: '/images/test1.jpg',
                created_at: new Date().toISOString(),
              },
              {
                id: 2,
                name: 'Test Human 2',
                description: 'Another test digital human',
                image_url: '/images/test2.jpg',
                created_at: new Date().toISOString(),
              },
            ],
            total: 2,
            page: 1,
            page_size: 10,
          });
        })
      );

      const result = await digitalHumanAPI.getDigitalHumans();

      expect(result.items).toHaveLength(2);
      expect(result.total).toBe(2);
      expect(result.items[0].name).toBe('Test Human 1');
    });

    it('should create a new digital human', async () => {
      // Mock create digital human response
      server.use(
        http.post('/api/v1/digital-human/create', () => {
          return HttpResponse.json({
            id: 3,
            name: 'New Digital Human',
            description: 'A newly created digital human',
            image_url: '/images/new.jpg',
            created_at: new Date().toISOString(),
          });
        })
      );

      const formData = new FormData();
      formData.append('name', 'New Digital Human');
      formData.append('description', 'A newly created digital human');

      const result = await digitalHumanAPI.createDigitalHuman(formData);

      expect(result.id).toBe(3);
      expect(result.name).toBe('New Digital Human');
    });

    it('should get digital human details', async () => {
      // Mock get digital human details response
      server.use(
        http.get('/api/v1/digital-human/:id', ({ params }) => {
          return HttpResponse.json({
            id: Number(params.id),
            name: 'Test Human',
            description: 'A test digital human',
            image_url: '/images/test.jpg',
            voice_profile_id: 'voice-123',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        })
      );

      const result = await digitalHumanAPI.getDigitalHuman(1);

      expect(result.id).toBe(1);
      expect(result.name).toBe('Test Human');
      expect(result.voice_profile_id).toBe('voice-123');
    });

    it('should delete a digital human', async () => {
      // Mock delete digital human response
      server.use(
        http.delete('/api/v1/digital-human/:id', () => {
          return HttpResponse.json({ message: 'Digital human deleted successfully' });
        })
      );

      await expect(digitalHumanAPI.deleteDigitalHuman(1)).resolves.not.toThrow();
    });

    it('should generate video for digital human', async () => {
      // Mock generate video response
      server.use(
        http.post('/api/v1/digital-human/generate', () => {
          return HttpResponse.json({
            task_id: 'task-123',
            status: 'pending',
            message: 'Video generation started',
          });
        })
      );

      const result = await digitalHumanAPI.generateVideo({
        digital_human_id: 1,
        text: 'Hello, this is a test video',
        mode: 'lipsync',
      });

      expect(result.task_id).toBe('task-123');
      expect(result.status).toBe('pending');
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
        http.get('/api/v1/plugins/list', () => {
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

      const result = await pluginsAPI.getPlugins();

      expect(result.plugins).toHaveLength(2);
      expect(result.plugins[0].name).toBe('image-processor');
      expect(result.plugins[1].name).toBe('video-editor');
    });

    it('should install a new plugin', async () => {
      // Mock install plugin response
      server.use(
        http.post('/api/v1/plugins/install', () => {
          return HttpResponse.json({
            name: 'new-plugin',
            version: '1.0.0',
            status: 'active',
            message: 'Plugin installed successfully',
          });
        })
      );

      const result = await pluginsAPI.installPlugin({
        name: 'new-plugin',
        version: '1.0.0',
      });

      expect(result.name).toBe('new-plugin');
      expect(result.status).toBe('active');
    });

    it('should reload a plugin', async () => {
      // Mock reload plugin response
      server.use(
        http.post('/api/v1/plugins/reload', () => {
          return HttpResponse.json({
            name: 'image-processor',
            status: 'active',
            message: 'Plugin reloaded successfully',
          });
        })
      );

      const result = await pluginsAPI.reloadPlugin('image-processor');

      expect(result.name).toBe('image-processor');
      expect(result.status).toBe('active');
    });

    it('should handle plugin installation failure', async () => {
      // Mock plugin installation failure
      server.use(
        http.post('/api/v1/plugins/install', () => {
          return HttpResponse.json(
            { detail: 'Plugin not found in registry' },
            { status: 404 }
          );
        })
      );

      await expect(
        pluginsAPI.installPlugin({
          name: 'non-existent-plugin',
          version: '1.0.0',
        })
      ).rejects.toThrow();
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle network errors', async () => {
      // Mock network error
      server.use(
        http.get('/api/v1/digital-human/list', () => {
          return HttpResponse.error();
        })
      );

      await expect(digitalHumanAPI.getDigitalHumans()).rejects.toThrow();
    });

    it('should handle 500 server errors', async () => {
      // Mock server error
      server.use(
        http.get('/api/v1/digital-human/list', () => {
          return HttpResponse.json(
            { detail: 'Internal server error' },
            { status: 500 }
          );
        })
      );

      await expect(digitalHumanAPI.getDigitalHumans()).rejects.toThrow();
    });

    it('should handle unauthorized requests', async () => {
      // Clear token
      localStorage.clear();

      // Mock unauthorized response
      server.use(
        http.get('/api/v1/digital-human/list', () => {
          return HttpResponse.json(
            { detail: 'Not authenticated' },
            { status: 401 }
          );
        })
      );

      await expect(digitalHumanAPI.getDigitalHumans()).rejects.toThrow();
    });
  });
});
