import {
  AlertCircle,
  Download,
  FileDown,
  Filter,
  Flag,
  Leaf,
  Loader2,
  RefreshCcw,
  Sparkles,
  XCircle,
} from "lucide-react"

import { BarChart } from "@/components/charts/bar-chart"
import { HeatmapChart } from "@/components/charts/heatmap-chart"
import { LineChart } from "@/components/charts/line-chart"
import { PieChart } from "@/components/charts/pie-chart"
import { ScatterChart } from "@/components/charts/scatter-chart"
import { ConditionSwitcher } from "@/components/condition-switcher"
import { IconLegend } from "@/components/icon-legend"
import { InsightsPanel } from "@/components/insights-panel"
import { KpiCard } from "@/components/kpi-card"
import { RecommendationsPanel } from "@/components/recommendations-panel"
import { StoryPanel } from "@/components/story-panel"
import { SurveyModal } from "@/components/survey-modal"
import { VoiceControls } from "@/components/voice-controls"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FilterSelect, type SelectOption } from "@/components/ui/filter-select"
import { useDashboard } from "@/hooks/use-dashboard"
import { useTaskLogger } from "@/hooks/use-task-logger"
import { useVoiceInput } from "@/hooks/use-voice-input"
import { useVoiceOutput } from "@/hooks/use-voice-output"
import { type ParsedIntent } from "@/lib/voice-intents"
import { useCallback, useEffect, useState } from "react"

function toOptions(values?: string[]): SelectOption[] {
  return (values ?? []).map((value) => ({ value, label: value }))
}

function Skeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6" aria-busy="true" aria-label="Loading dashboard">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="h-24 animate-pulse rounded-2xl bg-muted" />
      ))}
      <div className="col-span-full flex animate-pulse items-center justify-center rounded-2xl bg-muted py-24" />
      <div className="col-span-full h-48 animate-pulse rounded-2xl bg-muted" />
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-muted-foreground/30 bg-muted/20 p-12 text-center">
      <XCircle className="size-8 text-muted-foreground" aria-hidden="true" />
      <p className="text-sm font-medium text-foreground">No data available</p>
      <p className="text-xs text-muted-foreground">
        Try adjusting your filters or load a dataset to get started.
      </p>
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

  const [condition, setCondition] = useState("conventional")
  const [simpleMode, setSimpleMode] = useState(false)
  const [showSurvey, setShowSurvey] = useState(false)
  const [completedTasks, setCompletedTasks] = useState<Set<string>>(new Set())
  const [activeIcon, setActiveIcon] = useState<string | null>(null)
  const [userId] = useState(() => localStorage.getItem("agristory_user_id") || crypto.randomUUID())

  useEffect(() => {
    localStorage.setItem("agristory_user_id", userId)
  }, [userId])

  const voiceOutput = useVoiceOutput((wordIndex: number) => {
    if (!story?.story) return
    const words = story.story.split(/\s+/)
    const word = words[wordIndex]?.toLowerCase() ?? ""
    const iconMap: Record<string, string> = {
      rain: "rain", rainfall: "rain", precipitation: "rain",
      temperature: "temperature", temp: "temperature", heat: "temperature",
      humidity: "humidity", moisture: "humidity",
      yield: "sunny", production: "comparison",
      wind: "wind", forecast: "forecast",
      warning: "warning", alert: "warning",
      recommendation: "recommendation", action: "recommendation",
    }
    const iconId = iconMap[word]
    if (iconId) setActiveIcon(iconId)
  })
  const voiceInput = useVoiceInput()
  const { TASKS, startTask, completeTask } = useTaskLogger(condition, userId)

  const charts = dashboard?.charts
  const metadata = dashboard?.metadata
  const hasData = dashboard != null && (metadata?.rows ?? 0) > 0

  const handleVoiceIntent = useCallback(
    (intent: ParsedIntent) => {
      if (intent.action === "reset") {
        resetFilters()
      } else if (intent.action === "filter") {
        applyFilters({
          crop: intent.entities.crop ?? undefined,
          state: intent.entities.state ?? undefined,
          district: intent.entities.district ?? undefined,
          start_date: intent.entities.startDate ?? undefined,
          end_date: intent.entities.endDate ?? undefined,
        })
      }
    },
    [applyFilters, resetFilters]
  )

  const handleTaskStart = useCallback(
    (taskId: string) => {
      startTask(taskId)
    },
    [startTask]
  )

  const handleTaskComplete = useCallback(
    (taskId: string, completed: boolean = true, error?: string) => {
      completeTask(taskId, completed, error)
      setCompletedTasks((prev) => {
        const next = new Set(prev)
        next.add(taskId)
        return next
      })
      if (completed && completedTasks.size + 1 >= 3) {
        setTimeout(() => setShowSurvey(true), 500)
      }
    },
    [completeTask, completedTasks.size]
  )

  const handleSurveyComplete = useCallback(
    async (responses: { comprehension_score: number; trust_score: number; sus_score: number; feedback: string }) => {
      await fetch("/api/research/survey", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...responses, condition, user_id: userId }),
      })
      setShowSurvey(false)
    },
    [condition, userId]
  )

  const handleConditionChange = useCallback((newCondition: string) => {
    setCondition(newCondition)
    setCompletedTasks(new Set())
    voiceInput.resetContext()
  }, [voiceInput])

  const showVoiceControls = condition !== "conventional"
  const showIcons = condition === "voice-icons" || condition === "voice-story"
  const showStory = condition === "voice-story"

  return (
    <div className="mx-auto flex max-w-[1600px] flex-col gap-4 p-4 lg:p-8">
      {/* Header */}
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground" aria-hidden="true">
            <Leaf className="size-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">AgriStory Dashboard</h1>
            <p className="text-xs text-muted-foreground">
              Voice-Interactive Agricultural Data Storytelling — Research Prototype
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSurvey(true)}
            aria-label="Open research survey"
          >
            <Flag className="size-4" aria-hidden="true" />
            Survey ({completedTasks.size}/3)
          </Button>
          <Button variant="outline" size="sm" onClick={resetFilters} disabled={!hasFilters} aria-label="Reset all filters">
            <RefreshCcw className="size-4" aria-hidden="true" />
            Reset
          </Button>
          <Button variant="outline" size="sm" onClick={() => exportReport("json")} aria-label="Export dashboard as JSON">
            <FileDown className="size-4" aria-hidden="true" />
            JSON
          </Button>
          <Button size="sm" onClick={() => exportReport("pdf")} aria-label="Export dashboard as PDF">
            <Download className="size-4" aria-hidden="true" />
            Export PDF
          </Button>
        </div>
      </header>

      {/* Condition Switcher */}
      <ConditionSwitcher condition={condition} onConditionChange={handleConditionChange} />

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">
          <AlertCircle className="size-4 shrink-0" aria-hidden="true" />
          <span>{error}</span>
        </div>
      )}

      {/* Voice controls */}
      {showVoiceControls && (
        <VoiceControls
          onIntent={handleVoiceIntent}
          transcript={voiceInput.transcript}
          interimTranscript={voiceInput.interimTranscript}
          isListening={voiceInput.isListening}
          error={voiceInput.error}
          isSupported={voiceInput.isSupported}
          start={voiceInput.start}
          stop={voiceInput.stop}
          confirmation={voiceInput.confirmation}
          clarification={voiceInput.clarification}
        />
      )}

      {/* Icon legend / simple mode */}
      {showIcons && (
        <IconLegend
          simpleMode={simpleMode}
          onToggleSimple={() => setSimpleMode((v) => !v)}
          onReadAloud={() => {
            if (voiceOutput.isSpeaking) {
              voiceOutput.cancel()
              setActiveIcon(null)
            } else if (story?.story) {
              setActiveIcon(null)
              voiceOutput.speak(story.story)
            }
          }}
          isSpeaking={voiceOutput.isSpeaking}
          activeIcon={activeIcon}
        />
      )}

      {/* Filters */}
      <Card className="p-4">
        <CardHeader className="p-0 pb-3">
          <div className="flex items-center gap-2">
            <Filter className="size-4 text-primary" aria-hidden="true" />
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
            <label className="text-xs font-medium text-muted-foreground" htmlFor="start-date">
              Start Date
            </label>
            <input
              id="start-date"
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
            <label className="text-xs font-medium text-muted-foreground" htmlFor="end-date">
              End Date
            </label>
            <input
              id="end-date"
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

      {/* Task palette */}
      <Card className="p-3">
        <CardHeader className="p-0 pb-2">
          <div className="flex items-center gap-2">
            <Flag className="size-4 text-primary" aria-hidden="true" />
            <CardTitle className="text-sm">Research Tasks</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2 p-0">
          {TASKS.map((task) => {
            const done = completedTasks.has(task.id)
            return (
              <Button
                key={task.id}
                variant={done ? "default" : "outline"}
                size="sm"
                onClick={() => {
                  handleTaskStart(task.id)
                  setTimeout(() => handleTaskComplete(task.id, true), 3000)
                }}
                disabled={done}
              >
                {done ? "✓ " : ""}
                {task.label}
              </Button>
            )
          })}
        </CardContent>
      </Card>

      {loading ? (
        <Skeleton />
      ) : !hasData ? (
        <EmptyState />
      ) : (
        <>
          {/* KPIs */}
          {!simpleMode && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
              {dashboard?.kpis.map((kpi) => (
                <KpiCard key={kpi.label} kpi={kpi} />
              ))}
            </div>
          )}

          {/* Charts */}
          <div className={`grid gap-4 ${simpleMode ? "grid-cols-1" : "lg:grid-cols-2"}`}>
            {!simpleMode && (
              <>
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
              </>
            )}
            {simpleMode && (
              <Card className="lg:col-span-2">
                <CardContent className="p-4">
                  <PieChart
                    labels={charts?.pie.labels ?? []}
                    values={charts?.pie.values ?? []}
                    title="Crop Distribution (Simple View)"
                  />
                </CardContent>
              </Card>
            )}
          </div>

          {/* Insights + Story */}
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Sparkles className="size-4 text-primary" aria-hidden="true" />
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
                    aria-label="Regenerate insights"
                  >
                    <RefreshCcw className="size-4" aria-hidden="true" />
                    Refresh
                  </Button>
                )}
              </CardContent>
            </Card>
            {showStory && (
              <StoryPanel
                story={story}
                onRegenerate={regenerateStory}
                regenerating={storyLoading}
              />
            )}
          </div>

          {/* Recommendations */}
          {showStory && <RecommendationsPanel recommendations={recommendations} />}

          <footer className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {metadata?.rows != null && (
                <>
                  Showing <b className="text-foreground">{metadata.rows}</b>{" "}
                  record{metadata.rows === 1 ? "" : "s"}
                </>
              )}
            </span>
            <span className="inline-flex items-center gap-1.5">
              {story?.source === "ai" ? (
                <>Story powered by Gemini</>
              ) : (
                <>
                  <Loader2 className="size-3" aria-hidden="true" /> Rule-based analysis
                </>
              )}
            </span>
          </footer>
        </>
      )}

      {/* Survey Modal */}
      {showSurvey && (
        <SurveyModal
          condition={condition}
          onComplete={handleSurveyComplete}
          onSkip={() => setShowSurvey(false)}
        />
      )}
    </div>
  )
}
