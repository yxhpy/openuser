import { describe, it, expect, beforeEach, vi } from 'vitest';
import { storage, type User } from '../storage';
import { TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY } from '../constants';

describe('storage', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('getToken', () => {
    it('should return null when no token is stored', () => {
      expect(storage.getToken()).toBeNull();
    });

    it('should return the stored token', () => {
      localStorage.setItem(TOKEN_KEY, 'test-token');
      expect(storage.getToken()).toBe('test-token');
    });
  });

  describe('setToken', () => {
    it('should store the token in localStorage', () => {
      storage.setToken('new-token');
      expect(localStorage.getItem(TOKEN_KEY)).toBe('new-token');
    });

    it('should overwrite existing token', () => {
      storage.setToken('old-token');
      storage.setToken('new-token');
      expect(localStorage.getItem(TOKEN_KEY)).toBe('new-token');
    });
  });

  describe('getRefreshToken', () => {
    it('should return null when no refresh token is stored', () => {
      expect(storage.getRefreshToken()).toBeNull();
    });

    it('should return the stored refresh token', () => {
      localStorage.setItem(REFRESH_TOKEN_KEY, 'test-refresh-token');
      expect(storage.getRefreshToken()).toBe('test-refresh-token');
    });
  });

  describe('setRefreshToken', () => {
    it('should store the refresh token in localStorage', () => {
      storage.setRefreshToken('new-refresh-token');
      expect(localStorage.getItem(REFRESH_TOKEN_KEY)).toBe('new-refresh-token');
    });

    it('should overwrite existing refresh token', () => {
      storage.setRefreshToken('old-refresh-token');
      storage.setRefreshToken('new-refresh-token');
      expect(localStorage.getItem(REFRESH_TOKEN_KEY)).toBe('new-refresh-token');
    });
  });

  describe('getUser', () => {
    it('should return null when no user is stored', () => {
      expect(storage.getUser()).toBeNull();
    });

    it('should return the stored user object', () => {
      const user: User = {
        id: '123',
        username: 'testuser',
        email: 'test@example.com',
      };
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      expect(storage.getUser()).toEqual(user);
    });

    it('should return null when stored user data is invalid JSON', () => {
      localStorage.setItem(USER_KEY, 'invalid-json');
      expect(storage.getUser()).toBeNull();
    });

    it('should return null when stored user data is empty string', () => {
      localStorage.setItem(USER_KEY, '');
      expect(storage.getUser()).toBeNull();
    });
  });

  describe('setUser', () => {
    it('should store the user object as JSON in localStorage', () => {
      const user: User = {
        id: '456',
        username: 'newuser',
        email: 'new@example.com',
      };
      storage.setUser(user);
      const storedUser = localStorage.getItem(USER_KEY);
      expect(storedUser).toBe(JSON.stringify(user));
      expect(JSON.parse(storedUser!)).toEqual(user);
    });

    it('should overwrite existing user', () => {
      const oldUser: User = {
        id: '123',
        username: 'olduser',
        email: 'old@example.com',
      };
      const newUser: User = {
        id: '456',
        username: 'newuser',
        email: 'new@example.com',
      };
      storage.setUser(oldUser);
      storage.setUser(newUser);
      expect(storage.getUser()).toEqual(newUser);
    });
  });

  describe('clear', () => {
    it('should remove all stored data', () => {
      storage.setToken('test-token');
      storage.setRefreshToken('test-refresh-token');
      storage.setUser({
        id: '123',
        username: 'testuser',
        email: 'test@example.com',
      });

      storage.clear();

      expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
      expect(localStorage.getItem(REFRESH_TOKEN_KEY)).toBeNull();
      expect(localStorage.getItem(USER_KEY)).toBeNull();
    });

    it('should not throw error when clearing empty storage', () => {
      expect(() => storage.clear()).not.toThrow();
    });
  });
});
