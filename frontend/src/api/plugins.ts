import apiClient from './client';

export interface PluginInfo {
  name: string;
  version: string;
  dependencies: string[];
}

export interface PluginListResponse {
  plugins: PluginInfo[];
  total: number;
}

export interface PluginInstallRequest {
  name: string;
}

export interface PluginInstallResponse {
  name: string;
  version: string;
  message: string;
}

export interface PluginReloadRequest {
  name: string;
}

export interface PluginReloadResponse {
  name: string;
  version: string;
  message: string;
}

export const pluginApi = {
  /**
   * List all installed plugins
   */
  list: async (): Promise<PluginListResponse> => {
    const response = await apiClient.get<PluginListResponse>('/api/v1/plugins/list');
    return response.data;
  },

  /**
   * Install a new plugin
   */
  install: async (request: PluginInstallRequest): Promise<PluginInstallResponse> => {
    const response = await apiClient.post<PluginInstallResponse>('/api/v1/plugins/install', request);
    return response.data;
  },

  /**
   * Reload an existing plugin
   */
  reload: async (request: PluginReloadRequest): Promise<PluginReloadResponse> => {
    const response = await apiClient.post<PluginReloadResponse>('/api/v1/plugins/reload', request);
    return response.data;
  },
};
