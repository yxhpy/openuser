import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { server } from '../../test/mocks/server';
import { http, HttpResponse } from 'msw';
import { pluginApi, PluginListResponse, PluginInstallResponse, PluginReloadResponse } from '../plugins';
import { API_BASE_URL } from '../../utils/constants';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Plugin API', () => {
  describe('list', () => {
    it('should list all plugins successfully', async () => {
      const mockResponse: PluginListResponse = {
        plugins: [
          {
            name: 'image-processor',
            version: '1.0.0',
            dependencies: [],
          },
          {
            name: 'video-editor',
            version: '2.1.0',
            dependencies: ['ffmpeg'],
          },
        ],
        total: 2,
      };

      server.use(
        http.get(`${API_BASE_URL}/api/v1/plugins/list`, () => {
          return HttpResponse.json(mockResponse);
        })
      );

      const result = await pluginApi.list();

      expect(result).toEqual(mockResponse);
      expect(result.plugins).toHaveLength(2);
      expect(result.total).toBe(2);
    });

    it('should handle empty plugin list', async () => {
      const mockResponse: PluginListResponse = {
        plugins: [],
        total: 0,
      };

      server.use(
        http.get(`${API_BASE_URL}/api/v1/plugins/list`, () => {
          return HttpResponse.json(mockResponse);
        })
      );

      const result = await pluginApi.list();

      expect(result).toEqual(mockResponse);
      expect(result.plugins).toHaveLength(0);
      expect(result.total).toBe(0);
    });

    it('should handle authentication error', async () => {
      server.use(
        http.get(`${API_BASE_URL}/api/v1/plugins/list`, () => {
          return HttpResponse.json(
            { detail: 'Not authenticated' },
            { status: 401 }
          );
        })
      );

      await expect(pluginApi.list()).rejects.toThrow();
    });
  });

  describe('install', () => {
    it('should install plugin successfully', async () => {
      const mockResponse: PluginInstallResponse = {
        name: 'audio-enhancer',
        version: '1.5.0',
        message: "Plugin 'audio-enhancer' installed successfully",
      };

      server.use(
        http.post(`${API_BASE_URL}/api/v1/plugins/install`, () => {
          return HttpResponse.json(mockResponse);
        })
      );

      const result = await pluginApi.install({ name: 'audio-enhancer' });

      expect(result).toEqual(mockResponse);
      expect(result.name).toBe('audio-enhancer');
      expect(result.version).toBe('1.5.0');
      expect(result.message).toContain('installed successfully');
    });

    it('should handle plugin already installed error', async () => {
      server.use(
        http.post(`${API_BASE_URL}/api/v1/plugins/install`, () => {
          return HttpResponse.json(
            { detail: "Plugin 'image-processor' is already installed" },
            { status: 400 }
          );
        })
      );

      await expect(
        pluginApi.install({ name: 'image-processor' })
      ).rejects.toThrow();
    });

    it('should handle plugin not found error', async () => {
      server.use(
        http.post(`${API_BASE_URL}/api/v1/plugins/install`, () => {
          return HttpResponse.json(
            { detail: "Failed to install plugin 'non-existent'" },
            { status: 400 }
          );
        })
      );

      await expect(
        pluginApi.install({ name: 'non-existent' })
      ).rejects.toThrow();
    });
  });

  describe('reload', () => {
    it('should reload plugin successfully', async () => {
      const mockResponse: PluginReloadResponse = {
        name: 'image-processor',
        version: '1.0.1',
        message: "Plugin 'image-processor' reloaded successfully",
      };

      server.use(
        http.post(`${API_BASE_URL}/api/v1/plugins/reload`, () => {
          return HttpResponse.json(mockResponse);
        })
      );

      const result = await pluginApi.reload({ name: 'image-processor' });

      expect(result).toEqual(mockResponse);
      expect(result.name).toBe('image-processor');
      expect(result.message).toContain('reloaded successfully');
    });

    it('should handle plugin not found error', async () => {
      server.use(
        http.post(`${API_BASE_URL}/api/v1/plugins/reload`, () => {
          return HttpResponse.json(
            { detail: "Plugin 'non-existent' not found" },
            { status: 404 }
          );
        })
      );

      await expect(
        pluginApi.reload({ name: 'non-existent' })
      ).rejects.toThrow();
    });

    it('should handle reload failure', async () => {
      server.use(
        http.post(`${API_BASE_URL}/api/v1/plugins/reload`, () => {
          return HttpResponse.json(
            { detail: "Failed to reload plugin 'broken-plugin'" },
            { status: 400 }
          );
        })
      );

      await expect(
        pluginApi.reload({ name: 'broken-plugin' })
      ).rejects.toThrow();
    });
  });
});
