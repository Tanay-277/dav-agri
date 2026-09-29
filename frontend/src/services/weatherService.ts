import { apiRequest } from './apiClient';
import { AgriculturalWeather, LanguageCode } from '../types';

export const weatherService = {
  async getCurrentWeather(location?: string, language: LanguageCode = 'mr'): Promise<AgriculturalWeather> {
    const params = new URLSearchParams();
    if (location) params.append('location', location);
    params.append('language', language);
    return apiRequest<AgriculturalWeather>(`/weather/current?${params.toString()}`);
  },

  async getForecast(location?: string, language: LanguageCode = 'mr'): Promise<AgriculturalWeather> {
    const params = new URLSearchParams();
    if (location) params.append('location', location);
    params.append('language', language);
    return apiRequest<AgriculturalWeather>(`/weather/forecast?${params.toString()}`);
  },
};
