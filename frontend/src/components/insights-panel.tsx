import type { Insight } from "@/types/api"
import { AlertTriangle, Zap } from "lucide-react"
import {
  CloudIcon,
  ComparisonIcon,
  ForecastIcon,
  HumidityIcon,
  RainIcon,
  SunnyIcon,
  TemperatureIcon,
  TrendDownIcon,
  TrendUpIcon,
  WarningIcon,
  WindIcon,
} from "@/lib/icons"

const severityStyles: Record<string, string> = {
  critical:
    "border-rose-500/20 bg-rose-500/10 text-rose-600 dark:text-rose-400",
  warning:
    "border-amber-500/20 bg-amber-500/10 text-amber-600 dark:text-amber-400",
  info: "border-sky-500/20 bg-sky-500/10 text-sky-600 dark:text-sky-400",
}

function iconFor(insight: Insight) {
  if (
    insight.magnitude != null &&
    insight.magnitude < 0 &&
    insight.type !== "anomaly"
  ) {
    return TrendDownIcon
  }
  if (insight.magnitude != null && insight.magnitude > 0) {
    return TrendUpIcon
  }
  if (insight.type === "anomaly") {
    return Zap
  }
  if (insight.type === "comparison") {
    return ComparisonIcon
  }
  if (insight.message.toLowerCase().includes("rain")) return RainIcon
  if (insight.message.toLowerCase().includes("temperature") || insight.message.toLowerCase().includes("temp")) return TemperatureIcon
  if (insight.message.toLowerCase().includes("humidity") || insight.message.toLowerCase().includes("moisture")) return HumidityIcon
  if (insight.message.toLowerCase().includes("yield")) return SunnyIcon
  if (insight.message.toLowerCase().includes("wind")) return WindIcon
  if (insight.message.toLowerCase().includes("cloud")) return CloudIcon
  if (insight.message.toLowerCase().includes("forecast")) return ForecastIcon
  if (insight.message.toLowerCase().includes("warning") || insight.message.toLowerCase().includes("alert")) return WarningIcon
  return AlertTriangle
}

export function InsightsPanel({ insights }: { insights: Insight[] }) {
  return (
    <div className="flex flex-col gap-2.5">
      {insights.length === 0 && (
        <p className="text-sm text-muted-foreground">No insights detected.</p>
      )}
      {insights.map((insight, i) => {
        const Icon = iconFor(insight)
        const style = severityStyles[insight.severity] ?? severityStyles.info
        return (
          <div
            key={i}
            className={`flex items-start gap-2.5 rounded-xl border p-3 ${style}`}
          >
            <Icon className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <p className="text-sm leading-snug">{insight.message}</p>
          </div>
        )
      })}
    </div>
  )
}
