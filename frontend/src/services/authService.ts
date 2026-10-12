import { apiRequest } from './apiClient';
import { User } from '../types';

export const authService = {
  async register(username: string, password: string) {
    const res = await apiRequest<{
      access_token: string;
      user_id: string;
      phone?: string;
      onboarding_completed: boolean;
      preferred_language: string;
    }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    if (res.access_token) {
      localStorage.setItem('dav_auth_token', res.access_token);
    }
    return res;
  },

  async login(username: string, password: string) {
    const res = await apiRequest<{
      access_token: string;
      user_id: string;
      phone?: string;
      onboarding_completed: boolean;
      preferred_language: string;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
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
      username?: string;
      phone?: string;
      name: string;
      preferred_language: 'en' | 'hi' | 'mr';
      onboarding_completed: boolean;
    }>('/auth/me');
    return {
      id: data.user_id,
      username: data.username,
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
