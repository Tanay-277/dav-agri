import { apiRequest } from './apiClient';
import { QueryResult, ConversationHistoryItem, LanguageCode } from '../types';

export const queryService = {
  async executeQuery(text: string, language: LanguageCode = 'mr', crop?: string): Promise<QueryResult> {
    return apiRequest<QueryResult>('/query', {
      method: 'POST',
      body: JSON.stringify({ text, language, crop }),
    });
  },

  async getHistory(limit: number = 10): Promise<ConversationHistoryItem[]> {
    return apiRequest<ConversationHistoryItem[]>(`/query/history?limit=${limit}`);
  },

  async getSharedQuery(shareToken: string): Promise<QueryResult> {
    return apiRequest<QueryResult>(`/query/share/${encodeURIComponent(shareToken)}`);
  },
};
