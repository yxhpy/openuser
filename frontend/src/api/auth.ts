import client from './client';
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  RefreshTokenRequest,
  User,
} from '@/types/auth';

export const authApi = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await client.post<AuthResponse>('/api/v1/auth/login', data);
    return response.data;
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await client.post<AuthResponse>('/api/v1/auth/register', data);
    return response.data;
  },

  async refresh(data: RefreshTokenRequest): Promise<{ access_token: string }> {
    const response = await client.post<{ access_token: string }>(
      '/api/v1/auth/refresh',
      data
    );
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await client.get<User>('/api/v1/auth/me');
    return response.data;
  },
};
