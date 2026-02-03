import { apiClient } from './client';
import type {
  TaskCreateRequest,
  TaskUpdateRequest,
  TaskResponse,
  TaskListResponse,
} from '../types/generated';

/**
 * Create a new scheduled task
 */
export const createTask = async (data: TaskCreateRequest): Promise<TaskResponse> => {
  const response = await apiClient.post<TaskResponse>('/api/v1/scheduler/create', data);
  return response.data;
};

/**
 * Get list of tasks with optional filters
 */
export const listTasks = async (params?: {
  status?: string;
  task_type?: string;
}): Promise<TaskListResponse> => {
  const response = await apiClient.get<TaskListResponse>('/api/v1/scheduler/list', { params });
  return response.data;
};

/**
 * Get task details by ID
 */
export const getTask = async (taskId: number): Promise<TaskResponse> => {
  const response = await apiClient.get<TaskResponse>(`/api/v1/scheduler/${taskId}`);
  return response.data;
};

/**
 * Update a task
 */
export const updateTask = async (
  taskId: number,
  data: TaskUpdateRequest
): Promise<TaskResponse> => {
  const response = await apiClient.put<TaskResponse>(`/api/v1/scheduler/${taskId}`, data);
  return response.data;
};

/**
 * Delete a task
 */
export const deleteTask = async (taskId: number): Promise<void> => {
  await apiClient.delete(`/api/v1/scheduler/${taskId}`);
};
