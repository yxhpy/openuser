import client from './client';
import type {
  DigitalHuman,
  CreateDigitalHumanRequest,
  GenerateVideoRequest,
  GenerateVideoResponse,
  DigitalHumanListResponse,
} from '../types/digitalHuman';

/**
 * Create a new digital human
 */
export const createDigitalHuman = async (
  data: CreateDigitalHumanRequest
): Promise<DigitalHuman> => {
  const formData = new FormData();
  formData.append('name', data.name);
  if (data.description) {
    formData.append('description', data.description);
  }
  if (data.image) {
    formData.append('image', data.image);
  }

  const response = await client.post<DigitalHuman>(
    '/api/v1/digital-human/create',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

/**
 * Generate video from digital human
 */
export const generateVideo = async (
  data: GenerateVideoRequest
): Promise<GenerateVideoResponse> => {
  const formData = new FormData();
  formData.append('digital_human_id', data.digital_human_id.toString());
  formData.append('mode', data.mode);

  if (data.text) {
    formData.append('text', data.text);
  }
  if (data.audio) {
    formData.append('audio', data.audio);
  }
  if (data.speaker_wav) {
    formData.append('speaker_wav', data.speaker_wav);
  }

  const response = await client.post<GenerateVideoResponse>(
    '/api/v1/digital-human/generate',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

/**
 * Get list of digital humans
 */
export const listDigitalHumans = async (): Promise<DigitalHumanListResponse> => {
  const response = await client.get<DigitalHumanListResponse>(
    '/api/v1/digital-human/list'
  );
  return response.data;
};

/**
 * Get digital human by ID
 */
export const getDigitalHuman = async (id: number): Promise<DigitalHuman> => {
  const response = await client.get<DigitalHuman>(
    `/api/v1/digital-human/${id}`
  );
  return response.data;
};

/**
 * Delete digital human
 */
export const deleteDigitalHuman = async (id: number): Promise<void> => {
  await client.delete(`/api/v1/digital-human/${id}`);
};
