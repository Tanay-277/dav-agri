import { ArrowDownRight, ArrowUpRight } from "lucide-react"

import type { KPI } from "@/types/api"
import { Card } from "@/components/ui/card"
import {
  CloudIcon,
  ComparisonIcon,
  ForecastIcon,
  HumidityIcon,
  RainIcon,
  RainProbabilityIcon,
  RecommendationIcon,
  SunnyIcon,
  TemperatureIcon,
  TrendUpIcon,
  WarningIcon,
  WindIcon,
} from "@/lib/icons"

function formatValue(value: KPI["value"]) {
  if (value == null || value === "—") return "—"
  if (typeof value === "number") {
    if (Math.abs(value) >= 1_000_000)
      return value.toLocaleString(undefined, { maximumFractionDigits: 0 })
    if (Math.abs(value) >= 1_000)
      return value.toLocaleString(undefined, { maximumFractionDigits: 0 })
    if (Number.isInteger(value)) return value.toLocaleString()
    return value.toLocaleString(undefined, { maximumFractionDigits: 1 })
  }
  return String(value)
}

function iconForLabel(label: string) {
  const lower = label.toLowerCase()
  if (lower.includes("rain")) return RainIcon
  if (lower.includes("temperature") || lower.includes("temp")) return TemperatureIcon
  if (lower.includes("humidity") || lower.includes("moisture")) return HumidityIcon
  if (lower.includes("yield")) return SunnyIcon
  if (lower.includes("production")) return ComparisonIcon
  if (lower.includes("wind")) return WindIcon
  if (lower.includes("forecast")) return ForecastIcon
  if (lower.includes("recommendation") || lower.includes("action")) return RecommendationIcon
  if (lower.includes("warning") || lower.includes("alert")) return WarningIcon
  if (lower.includes("trend")) return TrendUpIcon
  if (lower.includes("cloud")) return CloudIcon
  return RainProbabilityIcon
}

interface KpiCardProps {
  kpi: KPI
  simpleMode?: boolean
}

export function KpiCard({ kpi, simpleMode }: KpiCardProps) {
  const change = kpi.change
  const isUp = change != null && change >= 0
  const Icon = iconForLabel(kpi.label)

  return (
    <Card className="flex flex-col gap-2 p-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        {/* eslint-disable-next-line react-hooks/static-components */}
        <Icon className="size-4 shrink-0" aria-hidden="true" />
        <span className="truncate font-medium">{kpi.label}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-semibold tracking-tight">
          {formatValue(kpi.value)}
        </span>
        {!simpleMode && kpi.unit && (
          <span className="text-sm text-muted-foreground">{kpi.unit}</span>
        )}
      </div>
      {!simpleMode && change != null && (
        <div
          className={`flex items-center gap-1 text-xs font-medium ${
            isUp
              ? "text-emerald-600 dark:text-emerald-400"
              : "text-rose-600 dark:text-rose-400"
          }`}
        >
          {isUp ? (
            <ArrowUpRight className="size-3.5" />
          ) : (
            <ArrowDownRight className="size-3.5" />
          )}
          <span>{Math.abs(change).toFixed(1)}%</span>
          <span className="text-muted-foreground">vs prev</span>
        </div>
      )}
    </Card>
  )
}
