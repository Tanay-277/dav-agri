import { apiRequest } from './apiClient';
import { User } from '../types';

export const authService = {
  async requestOtp(phone: string) {
    return apiRequest<{ phone: string; expires_in_seconds: number; message: string }>('/auth/phone/request-otp', {
      method: 'POST',
      body: JSON.stringify({ phone }),
    });
  },

  async verifyOtp(phone: string, otp: string) {
    const res = await apiRequest<{
      access_token: string;
      token_type: string;
      user_id: string;
      phone: string;
      onboarding_completed: boolean;
      preferred_language: string;
    }>('/auth/phone/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ phone, otp }),
    });

    if (res.access_token) {
      localStorage.setItem('dav_auth_token', res.access_token);
    }
    return res;
  },

  async googleAuth(idToken: string) {
    const res = await apiRequest<{
      access_token: string;
      user_id: string;
      onboarding_completed: boolean;
      preferred_language: string;
    }>('/auth/google', {
      method: 'POST',
      body: JSON.stringify({ id_token: idToken }),
    });

    if (res.access_token) {
      localStorage.setItem('dav_auth_token', res.access_token);
    }
    return res;
  },

  async getCurrentUser(): Promise<User> {
    const data = await apiRequest<{
      user_id: string;
      phone?: string;
      name: string;
      preferred_language: 'en' | 'hi' | 'mr';
      onboarding_completed: boolean;
    }>('/auth/me');

    return {
      id: data.user_id,
      phone: data.phone,
      name: data.name,
      preferred_language: data.preferred_language,
      onboarding_completed: data.onboarding_completed,
    };
  },

  logout() {
    localStorage.removeItem('dav_auth_token');
  },

  hasToken(): boolean {
    return Boolean(localStorage.getItem('dav_auth_token'));
  },
};
