export type LanguageCode = 'en' | 'hi' | 'mr';

export interface User {
  id: string;
  phone?: string;
  name: string;
  preferred_language: LanguageCode;
  onboarding_completed: boolean;
}

export interface Profile {
  id: string;
  user_id: string;
  name: string;
  location: string;
  age: number;
  avatar_url?: string;
  land_location: string;
  primary_crop: string;
  land_size: string;
  irrigation_type: string;
  livestock: string;
  crops_grown: string[];
  preferred_language: LanguageCode;
}

export interface Crop {
  id: string;
  name_en: string;
  name_hi: string;
  name_mr: string;
  season?: string;
  is_default: boolean;
}

export interface ProductionRecord {
  id: string;
  user_id: string;
  crop_id: string;
  crop_name: string;
  year: number;
  month?: number;
  quantity_quintals: number;
  revenue_inr: number;
  notes?: string;
  created_at: string;
}

export interface ExpenseItem {
  category: string;
  label_en: string;
  label_hi: string;
  label_mr: string;
  amount_inr: number;
  percentage: number;
  color: string;
}

export interface ExpenseBreakdown {
  total_expense_inr: number;
  breakdown: ExpenseItem[];
  labels: string[];
  percentages: number[];
  colors: string[];
}

export interface ChartDataset {
  name: string;
  color: string;
  data: number[];
}

export interface StructuredVisualization {
  type: 'stacked_bar' | 'line' | 'donut' | 'pie';
  title: string;
  unit?: string;
  labels: string[];
  datasets: ChartDataset[];
  raw_data?: Record<string, any>;
}

export interface TimeSlotForecast {
  period: string;
  label_en: string;
  label_hi: string;
  label_mr: string;
  temp_c: number;
  condition: string;
  rain_probability: number;
}

export interface AgriculturalWeather {
  location: string;
  temperature_c: number;
  condition: string;
  expected_rainfall_mm: number;
  duration_hours: number;
  intensity: string;
  intensity_level: number;
  irrigation_needed: boolean;
  irrigation_advisory_en: string;
  irrigation_advisory_hi: string;
  irrigation_advisory_mr: string;
  time_slots: TimeSlotForecast[];
}

export interface QueryResult {
  id: string;
  query: string;
  language: LanguageCode;
  intent: string;
  answer: string;
  visualization?: StructuredVisualization;
  sources: string[];
  share_token?: string;
  created_at: string;
}

export type QueryResponse = QueryResult;

export interface ConversationHistoryItem {
  id: string;
  query_text: string;
  query_language: LanguageCode;
  intent?: string;
  answer_text: string;
  visualization_data?: any;
  is_saved: boolean;
  share_token?: string;
  created_at: string;
}

export type ScreenId =
  | 'launch'
  | 'signup_options'
  | 'phone'
  | 'otp'
  | 'lang_select'
  | 'language_confirm'
  | 'voice_setup'
  | 'onboarded'
  | 'weather'
  | 'home'
  | 'listening'
  | 'processed'
  | 'farm'
  | 'farm_topic'
  | 'topic_explanation'
  | 'profile'
  | 'edit_profile';
