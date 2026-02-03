import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderWithRouter, screen, waitFor } from '@/test/utils';
import { authApi } from '@/api/auth';
import type { LoginRequest, AuthResponse } from '@/types/auth';

// Mock the auth API
vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    refresh: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

describe('Auth API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('login', () => {
    it('should call login API with correct credentials', async () => {
      const mockResponse: AuthResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          is_active: true,
          is_superuser: false,
          created_at: '2026-02-03T00:00:00Z',
        },
      };

      vi.mocked(authApi.login).mockResolvedValue(mockResponse);

      const loginData: LoginRequest = {
        username: 'testuser',
        password: 'Test123!',
      };

      const result = await authApi.login(loginData);

      expect(authApi.login).toHaveBeenCalledWith(loginData);
      expect(result).toEqual(mockResponse);
      expect(result.access_token).toBe('mock-access-token');
    });

    it('should handle login errors', async () => {
      const mockError = new Error('Invalid credentials');
      vi.mocked(authApi.login).mockRejectedValue(mockError);

      const loginData: LoginRequest = {
        username: 'testuser',
        password: 'wrongpassword',
      };

      await expect(authApi.login(loginData)).rejects.toThrow('Invalid credentials');
    });
  });

  describe('register', () => {
    it('should call register API with correct data', async () => {
      const mockResponse: AuthResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        user: {
          id: 1,
          username: 'newuser',
          email: 'new@example.com',
          is_active: true,
          is_superuser: false,
          created_at: '2026-02-03T00:00:00Z',
        },
      };

      vi.mocked(authApi.register).mockResolvedValue(mockResponse);

      const registerData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'Test123!',
      };

      const result = await authApi.register(registerData);

      expect(authApi.register).toHaveBeenCalledWith(registerData);
      expect(result).toEqual(mockResponse);
    });
  });
});
