import { apiRequest } from './apiClient';
import { LanguageCode } from '../types';

export const onboardingService = {
  async getStatus() {
    return apiRequest<{
      user_id: string;
      preferred_language: LanguageCode;
      voice_confirmed: boolean;
      onboarding_completed: boolean;
    }>('/onboarding/status');
  },

  async confirmLanguage(language: LanguageCode) {
    return apiRequest<{
      user_id: string;
      preferred_language: LanguageCode;
      voice_confirmed: boolean;
      onboarding_completed: boolean;
    }>('/onboarding/confirm-language', {
      method: 'POST',
      body: JSON.stringify({ language }),
    });
  },

  async updateOnboarding(updates: {
    preferred_language?: LanguageCode;
    voice_confirmed?: boolean;
    onboarding_completed?: boolean;
  }) {
    return apiRequest<{
      user_id: string;
      preferred_language: LanguageCode;
      voice_confirmed: boolean;
      onboarding_completed: boolean;
    }>('/onboarding', {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },
};
