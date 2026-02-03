import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  createDigitalHuman,
  generateVideo,
  listDigitalHumans,
  getDigitalHuman,
  deleteDigitalHuman,
} from '../digitalHuman';
import client from '../client';
import type {
  DigitalHuman,
  CreateDigitalHumanRequest,
  GenerateVideoRequest,
  GenerateVideoResponse,
  DigitalHumanListResponse,
} from '@/types/digitalHuman';

// Mock the client
vi.mock('../client', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('Digital Human API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createDigitalHuman', () => {
    it('should create digital human with name only', async () => {
      const mockResponse: DigitalHuman = {
        id: 1,
        user_id: 1,
        name: 'Test Human',
        description: undefined,
        image_path: undefined,
        voice_model_path: undefined,
        video_path: undefined,
        is_active: true,
        created_at: '2026-02-03T00:00:00Z',
        updated_at: '2026-02-03T00:00:00Z',
      };

      vi.mocked(client.post).mockResolvedValue({ data: mockResponse });

      const request: CreateDigitalHumanRequest = {
        name: 'Test Human',
      };

      const result = await createDigitalHuman(request);

      expect(client.post).toHaveBeenCalledWith(
        '/api/v1/digital-human/create',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      expect(result).toEqual(mockResponse);
    });

    it('should create digital human with all fields', async () => {
      const mockResponse: DigitalHuman = {
        id: 1,
        user_id: 1,
        name: 'Test Human',
        description: 'Test description',
        image_path: '/uploads/test.jpg',
        voice_model_path: undefined,
        video_path: undefined,
        is_active: true,
        created_at: '2026-02-03T00:00:00Z',
        updated_at: '2026-02-03T00:00:00Z',
      };

      vi.mocked(client.post).mockResolvedValue({ data: mockResponse });

      const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      const request: CreateDigitalHumanRequest = {
        name: 'Test Human',
        description: 'Test description',
        image: mockFile,
      };

      const result = await createDigitalHuman(request);

      expect(client.post).toHaveBeenCalled();
      const formData = vi.mocked(client.post).mock.calls[0][1] as FormData;
      expect(formData.get('name')).toBe('Test Human');
      expect(formData.get('description')).toBe('Test description');
      expect(formData.get('image')).toBe(mockFile);

      expect(result).toEqual(mockResponse);
    });

    it('should handle API errors', async () => {
      const errorMessage = 'Failed to create digital human';
      vi.mocked(client.post).mockRejectedValue(new Error(errorMessage));

      const request: CreateDigitalHumanRequest = {
        name: 'Test Human',
      };

      await expect(createDigitalHuman(request)).rejects.toThrow(errorMessage);
    });
  });

  describe('generateVideo', () => {
    it('should generate video with text', async () => {
      const mockResponse: GenerateVideoResponse = {
        video_path: '/uploads/video.mp4',
        message: 'Video generated successfully',
      };

      vi.mocked(client.post).mockResolvedValue({ data: mockResponse });

      const request: GenerateVideoRequest = {
        digital_human_id: 1,
        text: 'Hello world',
        mode: 'enhanced_talking_head',
      };

      const result = await generateVideo(request);

      expect(client.post).toHaveBeenCalledWith(
        '/api/v1/digital-human/generate',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      const formData = vi.mocked(client.post).mock.calls[0][1] as FormData;
      expect(formData.get('digital_human_id')).toBe('1');
      expect(formData.get('text')).toBe('Hello world');
      expect(formData.get('mode')).toBe('enhanced_talking_head');

      expect(result).toEqual(mockResponse);
    });

    it('should generate video with audio file', async () => {
      const mockResponse: GenerateVideoResponse = {
        video_path: '/uploads/video.mp4',
        message: 'Video generated successfully',
      };

      vi.mocked(client.post).mockResolvedValue({ data: mockResponse });

      const mockAudioFile = new File(['audio'], 'audio.mp3', { type: 'audio/mpeg' });
      const request: GenerateVideoRequest = {
        digital_human_id: 1,
        audio: mockAudioFile,
        mode: 'lipsync',
      };

      const result = await generateVideo(request);

      const formData = vi.mocked(client.post).mock.calls[0][1] as FormData;
      expect(formData.get('audio')).toBe(mockAudioFile);
      expect(formData.get('mode')).toBe('lipsync');

      expect(result).toEqual(mockResponse);
    });

    it('should generate video with speaker_wav', async () => {
      const mockResponse: GenerateVideoResponse = {
        video_path: '/uploads/video.mp4',
        message: 'Video generated successfully',
      };

      vi.mocked(client.post).mockResolvedValue({ data: mockResponse });

      const request: GenerateVideoRequest = {
        digital_human_id: 1,
        text: 'Hello',
        mode: 'enhanced_talking_head',
        speaker_wav: '/uploads/speaker.wav',
      };

      const result = await generateVideo(request);

      const formData = vi.mocked(client.post).mock.calls[0][1] as FormData;
      expect(formData.get('speaker_wav')).toBe('/uploads/speaker.wav');

      expect(result).toEqual(mockResponse);
    });

    it('should handle generation errors', async () => {
      const errorMessage = 'Video generation failed';
      vi.mocked(client.post).mockRejectedValue(new Error(errorMessage));

      const request: GenerateVideoRequest = {
        digital_human_id: 1,
        text: 'Hello',
        mode: 'enhanced_talking_head',
      };

      await expect(generateVideo(request)).rejects.toThrow(errorMessage);
    });
  });

  describe('listDigitalHumans', () => {
    it('should list all digital humans', async () => {
      const mockResponse: DigitalHumanListResponse = {
        digital_humans: [
          {
            id: 1,
            user_id: 1,
            name: 'Human 1',
            description: 'Description 1',
            image_path: '/uploads/1.jpg',
            voice_model_path: undefined,
            video_path: undefined,
            is_active: true,
            created_at: '2026-02-03T00:00:00Z',
            updated_at: '2026-02-03T00:00:00Z',
          },
          {
            id: 2,
            user_id: 1,
            name: 'Human 2',
            description: 'Description 2',
            image_path: '/uploads/2.jpg',
            voice_model_path: undefined,
            video_path: undefined,
            is_active: true,
            created_at: '2026-02-03T00:00:00Z',
            updated_at: '2026-02-03T00:00:00Z',
          },
        ],
        total: 2,
      };

      vi.mocked(client.get).mockResolvedValue({ data: mockResponse });

      const result = await listDigitalHumans();

      expect(client.get).toHaveBeenCalledWith('/api/v1/digital-human/list');
      expect(result).toEqual(mockResponse);
      expect(result.digital_humans).toHaveLength(2);
      expect(result.total).toBe(2);
    });

    it('should return empty list when no digital humans exist', async () => {
      const mockResponse: DigitalHumanListResponse = {
        digital_humans: [],
        total: 0,
      };

      vi.mocked(client.get).mockResolvedValue({ data: mockResponse });

      const result = await listDigitalHumans();

      expect(result.digital_humans).toHaveLength(0);
      expect(result.total).toBe(0);
    });

    it('should handle API errors', async () => {
      const errorMessage = 'Failed to fetch digital humans';
      vi.mocked(client.get).mockRejectedValue(new Error(errorMessage));

      await expect(listDigitalHumans()).rejects.toThrow(errorMessage);
    });
  });

  describe('getDigitalHuman', () => {
    it('should get digital human by id', async () => {
      const mockResponse: DigitalHuman = {
        id: 1,
        user_id: 1,
        name: 'Test Human',
        description: 'Test description',
        image_path: '/uploads/test.jpg',
        voice_model_path: undefined,
        video_path: undefined,
        is_active: true,
        created_at: '2026-02-03T00:00:00Z',
        updated_at: '2026-02-03T00:00:00Z',
      };

      vi.mocked(client.get).mockResolvedValue({ data: mockResponse });

      const result = await getDigitalHuman(1);

      expect(client.get).toHaveBeenCalledWith('/api/v1/digital-human/1');
      expect(result).toEqual(mockResponse);
    });

    it('should handle not found error', async () => {
      const errorMessage = 'Digital human not found';
      vi.mocked(client.get).mockRejectedValue(new Error(errorMessage));

      await expect(getDigitalHuman(999)).rejects.toThrow(errorMessage);
    });
  });

  describe('deleteDigitalHuman', () => {
    it('should delete digital human by id', async () => {
      vi.mocked(client.delete).mockResolvedValue({ data: {} });

      await deleteDigitalHuman(1);

      expect(client.delete).toHaveBeenCalledWith('/api/v1/digital-human/1');
    });

    it('should handle deletion errors', async () => {
      const errorMessage = 'Failed to delete digital human';
      vi.mocked(client.delete).mockRejectedValue(new Error(errorMessage));

      await expect(deleteDigitalHuman(1)).rejects.toThrow(errorMessage);
    });
  });
});
