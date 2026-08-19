import {
  AlertCircle,
  Download,
  FileDown,
  Filter,
  Leaf,
  Loader2,
  RefreshCcw,
  Sparkles,
} from "lucide-react"

import { BarChart } from "@/components/charts/bar-chart"
import { HeatmapChart } from "@/components/charts/heatmap-chart"
import { LineChart } from "@/components/charts/line-chart"
import { PieChart } from "@/components/charts/pie-chart"
import { ScatterChart } from "@/components/charts/scatter-chart"
import { InsightsPanel } from "@/components/insights-panel"
import { KpiCard } from "@/components/kpi-card"
import { RecommendationsPanel } from "@/components/recommendations-panel"
import { StoryPanel } from "@/components/story-panel"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FilterSelect, type SelectOption } from "@/components/ui/filter-select"
import { useDashboard } from "@/hooks/use-dashboard"

function toOptions(values?: string[]): SelectOption[] {
  return (values ?? []).map((value) => ({ value, label: value }))
}

function Skeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="h-24 animate-pulse rounded-2xl bg-muted" />
      ))}
      <div className="col-span-full flex animate-pulse items-center justify-center rounded-2xl bg-muted py-24" />
      <div className="col-span-full h-48 animate-pulse rounded-2xl bg-muted" />
    </div>
  )
}

export function DashboardPage() {
  const {
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
  } = useDashboard()

  const charts = dashboard?.charts
  const metadata = dashboard?.metadata

  return (
    <div className="mx-auto flex max-w-[1600px] flex-col gap-6 p-4 lg:p-8">
      {/* Header */}
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <Leaf className="size-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">
              AgriStory Dashboard
            </h1>
            <p className="text-sm text-muted-foreground">
              Interactive agricultural analytics with AI-driven insights
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={resetFilters}
            disabled={!hasFilters}
          >
            <RefreshCcw className="size-4" />
            Reset
          </Button>
          <Button variant="outline" onClick={() => exportReport("json")}>
            <FileDown className="size-4" />
            JSON
          </Button>
          <Button onClick={() => exportReport("pdf")}>
            <Download className="size-4" />
            Export PDF
          </Button>
        </div>
      </header>

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="size-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Filters */}
      <Card className="p-4">
        <CardHeader className="p-0 pb-3">
          <div className="flex items-center gap-2">
            <Filter className="size-4 text-primary" />
            <CardTitle>Filters</CardTitle>
            {activeFilterCount > 0 && (
              <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                {activeFilterCount} active
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent className="grid gap-4 p-0 sm:grid-cols-2 lg:grid-cols-5">
          <FilterSelect
            label="Crop"
            value={filters.crop ?? null}
            onChange={(v) => applyFilters({ crop: v })}
            options={toOptions(filterOptions.crop)}
          />
          <FilterSelect
            label="State"
            value={filters.state ?? null}
            onChange={(v) => applyFilters({ state: v })}
            options={toOptions(filterOptions.state)}
          />
          <FilterSelect
            label="District"
            value={filters.district ?? null}
            onChange={(v) => applyFilters({ district: v })}
            options={toOptions(filterOptions.district)}
          />
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-muted-foreground">
              Start Date
            </label>
            <input
              type="date"
              value={filters.start_date ?? ""}
              min={filterOptions.date_min ?? undefined}
              max={filters.end_date ?? filterOptions.date_max ?? undefined}
              onChange={(e) =>
                applyFilters({ start_date: e.target.value || null })
              }
              className="h-9 rounded-xl border border-input bg-background px-3 text-sm transition-colors outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/30 dark:bg-transparent"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-muted-foreground">
              End Date
            </label>
            <input
              type="date"
              value={filters.end_date ?? ""}
              min={filters.start_date ?? filterOptions.date_min ?? undefined}
              max={filterOptions.date_max ?? undefined}
              onChange={(e) =>
                applyFilters({ end_date: e.target.value || null })
              }
              className="h-9 rounded-xl border border-input bg-background px-3 text-sm transition-colors outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/30 dark:bg-transparent"
            />
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <Skeleton />
      ) : (
        <>
          {/* KPIs */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            {dashboard?.kpis.map((kpi) => (
              <KpiCard key={kpi.label} kpi={kpi} />
            ))}
          </div>

          {/* Charts */}
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardContent className="p-4">
                <LineChart
                  labels={charts?.line.labels ?? []}
                  series={charts?.line.series ?? []}
                  title={charts?.line.title}
                />
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <BarChart
                  labels={charts?.bar.labels ?? []}
                  values={charts?.bar.values ?? []}
                  title={charts?.bar.title}
                />
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <ScatterChart
                  points={charts?.scatter.points ?? []}
                  title={charts?.scatter.title}
                />
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <HeatmapChart
                  columns={charts?.heatmap.columns ?? []}
                  matrix={charts?.heatmap.matrix ?? []}
                  title={charts?.heatmap.title}
                />
              </CardContent>
            </Card>
            <Card className="lg:col-span-2">
              <CardContent className="p-4">
                <PieChart
                  labels={charts?.pie.labels ?? []}
                  values={charts?.pie.values ?? []}
                  title={charts?.pie.title}
                />
              </CardContent>
            </Card>
          </div>

          {/* Insights + Story */}
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Sparkles className="size-4 text-primary" />
                  <CardTitle>Automated Insights</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <InsightsPanel insights={insights} />
                {!error && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-3"
                    onClick={regenerateInsights}
                  >
                    <RefreshCcw className="size-4" />
                    Refresh
                  </Button>
                )}
              </CardContent>
            </Card>
            <StoryPanel
              story={story}
              onRegenerate={regenerateStory}
              regenerating={storyLoading}
            />
          </div>

          {/* Recommendations */}
          <RecommendationsPanel recommendations={recommendations} />

          <footer className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {metadata?.rows != null && (
                <>
                  Showing <b className="text-foreground">{metadata.rows}</b>{" "}
                  record
                  {metadata.rows === 1 ? "" : "s"}
                </>
              )}
            </span>
            <span className="inline-flex items-center gap-1.5">
              {story?.source === "ai" ? (
                <>Story powered by Gemini</>
              ) : (
                <>
                  <Loader2 className="size-3" /> Rule-based analysis
                </>
              )}
            </span>
          </footer>
        </>
      )}
    </div>
  )
}
