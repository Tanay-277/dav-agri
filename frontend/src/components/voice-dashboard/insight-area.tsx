import { AlertTriangle, Info, XCircle, Lightbulb } from "lucide-react"

import { SectionCard } from "@/components/voice-dashboard/section-card"

export interface InsightItem {
  id: string
  type: string
  message: string
  severity: "info" | "warning" | "critical"
  magnitude?: number | null
}

interface InsightAreaProps {
  insights: InsightItem[]
  loading: boolean
  error: string | null
}

const severityConfig = {
  info: {
    icon: <Info className="size-5" aria-hidden="true" />,
    bg: "bg-blue-50 border-blue-200",
    iconColor: "text-blue-600",
    textColor: "text-blue-900",
  },
  warning: {
    icon: <AlertTriangle className="size-5" aria-hidden="true" />,
    bg: "bg-orange-50 border-orange-200",
    iconColor: "text-orange-600",
    textColor: "text-orange-900",
  },
  critical: {
    icon: <XCircle className="size-5" aria-hidden="true" />,
    bg: "bg-red-50 border-red-200",
    iconColor: "text-red-600",
    textColor: "text-red-900",
  },
}

export function InsightArea({ insights, loading, error }: InsightAreaProps) {
  if (!insights.length && !loading && !error) {
    return (
      <SectionCard title="Insights" icon={<Lightbulb className="size-5" aria-hidden="true" />}>
        <p className="text-sm text-muted-foreground">Ask about crops or weather to see insights.</p>
      </SectionCard>
    )
  }

  return (
    <SectionCard
      title="Insights"
      icon={<Lightbulb className="size-5" aria-hidden="true" />}
      loading={loading}
      error={error}
    >
      {insights.length > 0 && (
        <div className="space-y-3">
          {insights.map((insight) => {
            const config = severityConfig[insight.severity]
            return (
              <div
                key={insight.id}
                className={`flex items-start gap-3 rounded-xl border p-4 ${config.bg}`}
              >
                <div className={`mt-0.5 ${config.iconColor}`}>{config.icon}</div>
                <div className="flex-1">
                  <p className={`text-sm font-medium ${config.textColor}`}>{insight.message}</p>
                  {insight.magnitude !== null && insight.magnitude !== undefined && (
                    <p className="mt-1 text-xs text-muted-foreground">
                      Impact: {insight.magnitude > 0 ? "+" : ""}
                      {insight.magnitude}
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </SectionCard>
  )
}
