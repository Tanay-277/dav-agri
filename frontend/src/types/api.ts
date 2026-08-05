export interface DashboardFilters {
  crop?: string | null
  state?: string | null
  district?: string | null
  start_date?: string | null
  end_date?: string | null
}

export interface KPI {
  label: string
  value: number | string | null
  unit?: string | null
  change?: number | null
  change_label?: string | null
}

export interface Series {
  name: string
  labels: string[]
  values: number[]
}

export interface BarChartData {
  title: string
  labels: string[]
  values: number[]
}

export interface ScatterChartData {
  title: string
  points: { x: number; y: number }[]
}

export interface HeatmapData {
  title: string
  columns: string[]
  matrix: number[][]
}

export interface PieChartData {
  title: string
  labels: string[]
  values: number[]
}

export interface ChartsData {
  line: { title: string; labels: string[]; series: Series[] }
  bar: BarChartData
  scatter: ScatterChartData
  heatmap: HeatmapData
  pie: PieChartData
}

export interface Insight {
  type: string
  metric?: string | null
  message: string
  severity: "info" | "warning" | "critical"
  magnitude?: number | null
}

export interface Recommendation {
  condition: string
  message: string
  priority: "low" | "medium" | "high"
  action?: string | null
}

export interface Story {
  story: string
  summary: string
  reasons: string[]
  recommendations: string[]
  source: "rule" | "ai"
}

export interface FilterOptions {
  crop?: string[]
  state?: string[]
  district?: string[]
  date_min?: string | null
  date_max?: string | null
  loaded: boolean
}

export interface DashboardResponse {
  charts: ChartsData
  kpis: KPI[]
  filters: FilterOptions
  metadata: { rows: number }
}

export interface InsightsResponse {
  insights: Insight[]
}

export interface RecommendationsResponse {
  recommendations: Recommendation[]
}
