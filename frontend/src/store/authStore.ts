import { create } from 'zustand';
import { authApi } from '@/api/auth';
import { storage, type User } from '@/utils/storage';
import type { LoginRequest, RegisterRequest } from '@/types/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: storage.getUser(),
  isAuthenticated: !!storage.getToken(),
  isLoading: false,
  error: null,

  login: async (data: LoginRequest) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authApi.login(data);
      storage.setToken(response.access_token);
      storage.setRefreshToken(response.refresh_token);
      storage.setUser(response.user);
      set({ user: response.user, isAuthenticated: true, isLoading: false });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Login failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  register: async (data: RegisterRequest) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authApi.register(data);
      storage.setToken(response.access_token);
      storage.setRefreshToken(response.refresh_token);
      storage.setUser(response.user);
      set({ user: response.user, isAuthenticated: true, isLoading: false });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Registration failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  logout: () => {
    storage.clear();
    set({ user: null, isAuthenticated: false, error: null });
  },

  checkAuth: async () => {
    const token = storage.getToken();
    if (!token) {
      set({ user: null, isAuthenticated: false });
      return;
    }

    try {
      const user = await authApi.getCurrentUser();
      storage.setUser(user);
      set({ user, isAuthenticated: true });
    } catch {
      storage.clear();
      set({ user: null, isAuthenticated: false });
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
