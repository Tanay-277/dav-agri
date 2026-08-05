import { api } from "@/services/api"
import type {
  DashboardFilters,
  DashboardResponse,
  FilterOptions,
  InsightsResponse,
  RecommendationsResponse,
  Story,
} from "@/types/api"

function toQuery(filters: DashboardFilters): URLSearchParams {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value != null && value !== "") params.set(key, String(value))
  }
  return params
}

export async function getDashboard(
  filters: DashboardFilters = {}
): Promise<DashboardResponse> {
  const { data } = await api.get<DashboardResponse>("/dashboard", {
    params: toQuery(filters),
  })
  return data
}

export async function getFilters(): Promise<FilterOptions> {
  const { data } = await api.get<FilterOptions>("/filters")
  return data
}

export async function getInsights(
  filters: DashboardFilters = {}
): Promise<InsightsResponse> {
  const { data } = await api.get<InsightsResponse>("/insights", {
    params: toQuery(filters),
  })
  return data
}

export async function getStory(
  filters: DashboardFilters = {}
): Promise<Story> {
  const { data } = await api.get<Story>("/story", {
    params: toQuery(filters),
  })
  return data
}

export async function getRecommendations(
  filters: DashboardFilters = {}
): Promise<RecommendationsResponse> {
  const { data } = await api.get<RecommendationsResponse>("/recommendations", {
    params: toQuery(filters),
  })
  return data
}

export async function exportDashboard(
  filters: DashboardFilters = {},
  format: "pdf" | "json" = "pdf"
): Promise<Blob> {
  const { data } = await api.post<Blob>("/export", null, {
    params: { ...toQuery(filters), format },
    responseType: "blob",
  })
  return data
}

export async function getDatasetStatus(): Promise<{
  loaded: boolean
  rows: number
  columns: string[]
}> {
  const { data } = await api.get("/dataset/status")
  return data
}
