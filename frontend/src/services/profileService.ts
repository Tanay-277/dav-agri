import { apiRequest } from './apiClient';
import { Profile } from '../types';

export const profileService = {
  async getProfile(): Promise<Profile> {
    return apiRequest<Profile>('/profile');
  },

  async updateProfile(updates: Partial<Profile>): Promise<Profile> {
    return apiRequest<Profile>('/profile', {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },
};
