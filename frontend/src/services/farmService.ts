import { apiRequest } from './apiClient';
import {
  Crop,
  ProductionRecord,
  ExpenseBreakdown,
  StructuredVisualization,
  ConversationHistoryItem,
  LanguageCode,
} from '../types';

export const farmService = {
  async listCrops(): Promise<Crop[]> {
    return apiRequest<Crop[]>('/farm/crops');
  },

  async getSummary() {
    return apiRequest<{
      primary_crop: string;
      total_land_size: string;
      total_production_quintals: number;
      total_expenses_inr: number;
      active_crops: Crop[];
      recent_records: ProductionRecord[];
    }>('/farm/summary');
  },

  async listProduction(cropId?: string): Promise<ProductionRecord[]> {
    const q = cropId ? `?crop_id=${encodeURIComponent(cropId)}` : '';
    return apiRequest<ProductionRecord[]>(`/farm/production${q}`);
  },

  async addProduction(data: {
    crop_id: string;
    year: number;
    month?: number;
    quantity_quintals: number;
    revenue_inr?: number;
    notes?: string;
  }): Promise<ProductionRecord> {
    return apiRequest<ProductionRecord>('/farm/production', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async addExpense(data: {
    category: string;
    amount_inr: number;
    crop_id?: string;
    notes?: string;
  }) {
    return apiRequest('/farm/expenses', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getExpenseBreakdown(cropId?: string, language: LanguageCode = 'mr'): Promise<ExpenseBreakdown> {
    const params = new URLSearchParams();
    if (cropId) params.append('crop_id', cropId);
    params.append('language', language);
    return apiRequest<ExpenseBreakdown>(`/farm/expenses/breakdown?${params.toString()}`);
  },

  async getCropIncomeTrends(language: LanguageCode = 'mr'): Promise<StructuredVisualization> {
    return apiRequest<StructuredVisualization>(`/farm/analytics/crop-income?language=${language}`);
  },

  async getConversations(limit: number = 10): Promise<ConversationHistoryItem[]> {
    return apiRequest<ConversationHistoryItem[]>(`/farm/conversations?limit=${limit}`);
  },
};
