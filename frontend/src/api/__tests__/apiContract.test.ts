import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { server } from '@/test/mocks/server';
import { http, HttpResponse } from 'msw';
import { authApi } from '@/api/auth';
import { listDigitalHumans, getDigitalHuman } from '@/api/digitalHuman';
import type { LoginRequest, RegisterRequest } from '@/types/auth';

/**
 * API Contract Tests
 *
 * These tests validate that frontend API calls match backend expectations.
 * They ensure:
 * 1. Request payloads match backend schemas
 * 2. Response structures match frontend types
 * 3. Error responses are handled correctly
 * 4. Required fields are present
 */

describe('API Contract Tests', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  describe('Auth API Contract', () => {
    describe('POST /api/v1/auth/login', () => {
      it('should send correct request payload', async () => {
        let capturedRequest: any;

        server.use(
          http.post('http://localhost:8000/api/v1/auth/login', async ({ request }) => {
            capturedRequest = await request.json();
            return HttpResponse.json({
              access_token: 'token',
              refresh_token: 'refresh',
              token_type: 'bearer',
              expires_in: 3600,
              user: {
                id: 1,
                username: 'test',
                email: 'test@example.com',
                is_active: true,
                is_superuser: false,
                created_at: '2026-02-03T00:00:00Z',
              },
            });
          })
        );

        const loginData: LoginRequest = {
          username: 'testuser',
          password: 'Test123!',
        };

        await authApi.login(loginData);

        // Validate request structure matches backend expectations
        expect(capturedRequest).toHaveProperty('username');
        expect(capturedRequest).toHaveProperty('password');
        expect(capturedRequest.username).toBe('testuser');
        expect(capturedRequest.password).toBe('Test123!');

        // Ensure no extra fields are sent
        const expectedKeys = ['username', 'password'];
        const actualKeys = Object.keys(capturedRequest);
        expect(actualKeys.sort()).toEqual(expectedKeys.sort());
      });

      it('should receive response matching AuthResponse type', async () => {
        server.use(
          http.post('http://localhost:8000/api/v1/auth/login', () => {
            return HttpResponse.json({
              access_token: 'mock-token',
              refresh_token: 'mock-refresh',
              token_type: 'bearer',
              expires_in: 3600,
              user: {
                id: 1,
                username: 'testuser',
                email: 'test@example.com',
                is_active: true,
                is_superuser: false,
                created_at: '2026-02-03T00:00:00Z',
              },
            });
          })
        );

        const result = await authApi.login({
          username: 'testuser',
          password: 'Test123!',
        });

        // Validate response structure matches AuthResponse type
        expect(result).toHaveProperty('access_token');
        expect(result).toHaveProperty('refresh_token');
        expect(result).toHaveProperty('token_type');
        expect(result).toHaveProperty('user');

        // Validate user structure
        expect(result.user).toHaveProperty('id');
        expect(result.user).toHaveProperty('username');
        expect(result.user).toHaveProperty('email');
        expect(result.user).toHaveProperty('is_active');
        expect(result.user).toHaveProperty('is_superuser');
        expect(result.user).toHaveProperty('created_at');

        // Type assertions
        expect(typeof result.access_token).toBe('string');
        expect(typeof result.refresh_token).toBe('string');
        expect(typeof result.token_type).toBe('string');
        expect(typeof result.user.id).toBe('number');
        expect(typeof result.user.username).toBe('string');
        expect(typeof result.user.email).toBe('string');
        expect(typeof result.user.is_active).toBe('boolean');
        expect(typeof result.user.is_superuser).toBe('boolean');
      });

      it('should handle 401 error response', async () => {
        server.use(
          http.post('http://localhost:8000/api/v1/auth/login', () => {
            return HttpResponse.json(
              { error: 'Invalid credentials' },
              { status: 401 }
            );
          })
        );

        await expect(
          authApi.login({ username: 'test', password: 'wrong' })
        ).rejects.toThrow();
      });
    });

    describe('POST /api/v1/auth/register', () => {
      it('should send correct request payload', async () => {
        let capturedRequest: any;

        server.use(
          http.post('http://localhost:8000/api/v1/auth/register', async ({ request }) => {
            capturedRequest = await request.json();
            return HttpResponse.json({
              access_token: 'token',
              refresh_token: 'refresh',
              token_type: 'bearer',
              expires_in: 3600,
              user: {
                id: 1,
                username: capturedRequest.username,
                email: capturedRequest.email,
                is_active: true,
                is_superuser: false,
                created_at: '2026-02-03T00:00:00Z',
              },
            });
          })
        );

        const registerData: RegisterRequest = {
          username: 'newuser',
          email: 'new@example.com',
          password: 'Test123!',
        };

        await authApi.register(registerData);

        // Validate request structure matches backend expectations
        expect(capturedRequest).toHaveProperty('username');
        expect(capturedRequest).toHaveProperty('email');
        expect(capturedRequest).toHaveProperty('password');
        expect(capturedRequest.username).toBe('newuser');
        expect(capturedRequest.email).toBe('new@example.com');

        // Ensure required fields are present
        const requiredKeys = ['username', 'email', 'password'];
        requiredKeys.forEach(key => {
          expect(capturedRequest).toHaveProperty(key);
        });
      });

      it('should validate email format in request', async () => {
        let capturedRequest: any;

        server.use(
          http.post('http://localhost:8000/api/v1/auth/register', async ({ request }) => {
            capturedRequest = await request.json();
            return HttpResponse.json({
              access_token: 'token',
              refresh_token: 'refresh',
              token_type: 'bearer',
              expires_in: 3600,
              user: {
                id: 1,
                username: 'test',
                email: capturedRequest.email,
                is_active: true,
                is_superuser: false,
                created_at: '2026-02-03T00:00:00Z',
              },
            });
          })
        );

        await authApi.register({
          username: 'test',
          email: 'test@example.com',
          password: 'Test123!',
        });

        // Validate email format
        expect(capturedRequest.email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
      });
    });
  });

  describe('Digital Human API Contract', () => {
    describe('GET /api/v1/digital-human/list', () => {
      it('should receive response matching DigitalHumanListResponse type', async () => {
        server.use(
          http.get('http://localhost:8000/api/v1/digital-human/list', () => {
            return HttpResponse.json({
              digital_humans: [
                {
                  id: 1,
                  user_id: 1,
                  name: 'Human 1',
                  description: 'Description 1',
                  image_path: '/uploads/1.jpg',
                  voice_model_path: null,
                  video_path: null,
                  is_active: true,
                  created_at: '2026-02-03T00:00:00Z',
                  updated_at: '2026-02-03T00:00:00Z',
                },
              ],
              total: 1,
            });
          })
        );

        const result = await listDigitalHumans();

        // Validate response structure
        expect(result).toHaveProperty('digital_humans');
        expect(result).toHaveProperty('total');
        expect(Array.isArray(result.digital_humans)).toBe(true);
        expect(typeof result.total).toBe('number');

        // Validate array items structure
        if (result.digital_humans.length > 0) {
          const item = result.digital_humans[0];
          expect(item).toHaveProperty('id');
          expect(item).toHaveProperty('user_id');
          expect(item).toHaveProperty('name');
          expect(item).toHaveProperty('is_active');
          expect(item).toHaveProperty('created_at');
          expect(item).toHaveProperty('updated_at');

          // Type assertions
          expect(typeof item.id).toBe('number');
          expect(typeof item.user_id).toBe('number');
          expect(typeof item.name).toBe('string');
          expect(typeof item.is_active).toBe('boolean');
        }
      });

      it('should handle empty list response', async () => {
        server.use(
          http.get('http://localhost:8000/api/v1/digital-human/list', () => {
            return HttpResponse.json({
              digital_humans: [],
              total: 0,
            });
          })
        );

        const result = await listDigitalHumans();

        expect(result.digital_humans).toEqual([]);
        expect(result.total).toBe(0);
      });
    });

    describe('GET /api/v1/digital-human/:id', () => {
      it('should receive response matching DigitalHuman type', async () => {
        server.use(
          http.get('http://localhost:8000/api/v1/digital-human/1', () => {
            return HttpResponse.json({
              id: 1,
              user_id: 1,
              name: 'Test Human',
              description: 'Test description',
              image_path: '/uploads/test.jpg',
              voice_model_path: null,
              video_path: null,
              is_active: true,
              created_at: '2026-02-03T00:00:00Z',
              updated_at: '2026-02-03T00:00:00Z',
            });
          })
        );

        const result = await getDigitalHuman(1);

        // Validate all required fields are present
        const requiredFields = [
          'id', 'user_id', 'name', 'is_active',
          'created_at', 'updated_at'
        ];

        requiredFields.forEach(field => {
          expect(result).toHaveProperty(field);
        });

        // Validate types
        expect(typeof result.id).toBe('number');
        expect(typeof result.user_id).toBe('number');
        expect(typeof result.name).toBe('string');
        expect(typeof result.is_active).toBe('boolean');
        expect(typeof result.created_at).toBe('string');
        expect(typeof result.updated_at).toBe('string');
      });
    });
  });

  describe('Error Response Contract', () => {
    it('should handle validation error response', async () => {
      server.use(
        http.post('http://localhost:8000/api/v1/auth/register', () => {
          return HttpResponse.json(
            {
              error: 'Validation error',
              detail: 'Password must contain at least one uppercase letter',
            },
            { status: 422 }
          );
        })
      );

      await expect(
        authApi.register({
          username: 'test',
          email: 'test@example.com',
          password: 'weak',
        })
      ).rejects.toThrow();
    });
  });
});
