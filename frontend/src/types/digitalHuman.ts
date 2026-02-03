// Digital Human Types

export interface DigitalHuman {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  image_path?: string;
  voice_model_path?: string;
  video_path?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateDigitalHumanRequest {
  name: string;
  description?: string;
  image?: File;
}

export interface GenerateVideoRequest {
  digital_human_id: number;
  text?: string;
  audio?: File;
  mode: 'lipsync' | 'talking_head' | 'enhanced_lipsync' | 'enhanced_talking_head';
  speaker_wav?: string;
}

export interface GenerateVideoResponse {
  video_path: string;
  message: string;
}

export interface DigitalHumanListResponse {
  digital_humans: DigitalHuman[];
  total: number;
}
