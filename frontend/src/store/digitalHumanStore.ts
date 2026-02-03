import { create } from 'zustand';
import type {
  DigitalHuman,
  CreateDigitalHumanRequest,
  GenerateVideoRequest,
} from '../types/digitalHuman';
import * as digitalHumanApi from '../api/digitalHuman';

interface DigitalHumanState {
  digitalHumans: DigitalHuman[];
  currentDigitalHuman: DigitalHuman | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchDigitalHumans: () => Promise<void>;
  fetchDigitalHuman: (id: number) => Promise<void>;
  createDigitalHuman: (data: CreateDigitalHumanRequest) => Promise<DigitalHuman>;
  deleteDigitalHuman: (id: number) => Promise<void>;
  generateVideo: (data: GenerateVideoRequest) => Promise<string>;
  clearError: () => void;
}

export const useDigitalHumanStore = create<DigitalHumanState>((set) => ({
  digitalHumans: [],
  currentDigitalHuman: null,
  loading: false,
  error: null,

  fetchDigitalHumans: async () => {
    set({ loading: true, error: null });
    try {
      const response = await digitalHumanApi.listDigitalHumans();
      set({ digitalHumans: response.digital_humans, loading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch digital humans',
        loading: false,
      });
    }
  },

  fetchDigitalHuman: async (id: number) => {
    set({ loading: true, error: null });
    try {
      const digitalHuman = await digitalHumanApi.getDigitalHuman(id);
      set({ currentDigitalHuman: digitalHuman, loading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch digital human',
        loading: false,
      });
    }
  },

  createDigitalHuman: async (data: CreateDigitalHumanRequest) => {
    set({ loading: true, error: null });
    try {
      const digitalHuman = await digitalHumanApi.createDigitalHuman(data);
      set((state) => ({
        digitalHumans: [...state.digitalHumans, digitalHuman],
        loading: false,
      }));
      return digitalHuman;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to create digital human',
        loading: false,
      });
      throw error;
    }
  },

  deleteDigitalHuman: async (id: number) => {
    set({ loading: true, error: null });
    try {
      await digitalHumanApi.deleteDigitalHuman(id);
      set((state) => ({
        digitalHumans: state.digitalHumans.filter((dh) => dh.id !== id),
        loading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to delete digital human',
        loading: false,
      });
      throw error;
    }
  },

  generateVideo: async (data: GenerateVideoRequest) => {
    set({ loading: true, error: null });
    try {
      const response = await digitalHumanApi.generateVideo(data);
      set({ loading: false });
      return response.video_path;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to generate video',
        loading: false,
      });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
