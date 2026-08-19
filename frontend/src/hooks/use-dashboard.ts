import { useCallback, useEffect, useRef, useState } from "react"

import {
  exportDashboard,
  getDashboard,
  getFilters,
  getInsights,
  getRecommendations,
  getStory,
} from "@/services/dashboard"
import type {
  DashboardFilters,
  DashboardResponse,
  FilterOptions,
  Insight,
  Recommendation,
  Story,
} from "@/types/api"

export interface DashboardState {
  filters: DashboardFilters
  filterOptions: FilterOptions
  dashboard: DashboardResponse | null
  insights: Insight[]
  story: Story | null
  recommendations: Recommendation[]
  loading: boolean
  error: string | null
  hasFilters: boolean
  activeFilterCount: number
}

export function useDashboard() {
  const [filters, setFilters] = useState<DashboardFilters>({})
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    loaded: false,
  })
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null)
  const [insights, setInsights] = useState<Insight[]>([])
  const [story, setStory] = useState<Story | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [storyLoading, setStoryLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const activeFilterCount = Object.values(filters).filter(
    (v) => v != null && v !== ""
  ).length
  const hasFilters = activeFilterCount > 0

  const load = useCallback(async (nextFilters: DashboardFilters) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    setLoading(true)
    setError(null)
    try {
      const [dash, ins, rec, st] = await Promise.all([
        getDashboard(nextFilters),
        getInsights(nextFilters),
        getRecommendations(nextFilters),
        getStory(nextFilters),
      ])
      if (controller.signal.aborted) return
      setDashboard(dash)
      setInsights(ins.insights)
      setRecommendations(rec.recommendations)
      setStory(st)
    } catch (err) {
      if (controller.signal.aborted) return
      setError(
        err instanceof Error ? err.message : "Failed to load dashboard data"
      )
    } finally {
      if (!controller.signal.aborted) setLoading(false)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    getFilters()
      .then((opts) => {
        if (!cancelled) setFilterOptions(opts)
        if (!cancelled) return load({})
      })
      .catch((err) => {
        if (!cancelled)
          setError(
            err instanceof Error ? err.message : "Failed to load filters"
          )
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
      abortRef.current?.abort()
    }
  }, [load])

  const applyFilters = useCallback(
    (patch: Partial<DashboardFilters>) => {
      const merged = { ...filters, ...patch }
      setFilters(merged)
      void load(merged)
    },
    [filters, load]
  )

  const resetFilters = useCallback(() => {
    setFilters({})
    void load({})
  }, [load])

  const regenerateStory = useCallback(async () => {
    setStoryLoading(true)
    setError(null)
    try {
      const st = await getStory(filters)
      setStory(st)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to regenerate story"
      )
    } finally {
      setStoryLoading(false)
    }
  }, [filters])

  const regenerateInsights = useCallback(async () => {
    try {
      const res = await getInsights(filters)
      setInsights(res.insights)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load insights")
    }
  }, [filters])

  const exportReport = useCallback(
    async (format: "pdf" | "json" = "pdf") => {
      const blob = await exportDashboard(filters, format)
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement("a")
      anchor.href = url
      anchor.download = `agristory-report.${format}`
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      URL.revokeObjectURL(url)
    },
    [filters]
  )

  return {
    filters,
    filterOptions,
    dashboard,
    insights,
    story,
    recommendations,
    loading,
    storyLoading,
    error,
    hasFilters,
    activeFilterCount,
    applyFilters,
    resetFilters,
    regenerateStory,
    regenerateInsights,
    exportReport,
  }
}
