import { apiClient } from './client';
import type {
  AgentCreateRequest,
  AgentUpdateRequest,
  AgentResponse,
  AgentListResponse,
} from '../types/generated';

/**
 * Create a new agent
 */
export const createAgent = async (data: AgentCreateRequest): Promise<AgentResponse> => {
  const response = await apiClient.post<AgentResponse>('/api/v1/agents/create', data);
  return response.data;
};

/**
 * Get list of agents
 */
export const listAgents = async (): Promise<AgentListResponse> => {
  const response = await apiClient.get<AgentListResponse>('/api/v1/agents/list');
  return response.data;
};

/**
 * Get agent details by name
 */
export const getAgent = async (name: string): Promise<AgentResponse> => {
  const response = await apiClient.get<AgentResponse>(`/api/v1/agents/${name}`);
  return response.data;
};

/**
 * Update an agent
 */
export const updateAgent = async (
  name: string,
  data: AgentUpdateRequest
): Promise<AgentResponse> => {
  const response = await apiClient.put<AgentResponse>(`/api/v1/agents/${name}`, data);
  return response.data;
};

/**
 * Delete an agent
 */
export const deleteAgent = async (name: string): Promise<void> => {
  await apiClient.delete(`/api/v1/agents/${name}`);
};
