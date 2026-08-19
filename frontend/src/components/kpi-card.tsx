import { ArrowDownRight, ArrowUpRight } from "lucide-react"

import type { KPI } from "@/types/api"
import { Card } from "@/components/ui/card"

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

export function KpiCard({ kpi }: { kpi: KPI }) {
  const change = kpi.change
  const isUp = change != null && change >= 0

  return (
    <Card className="flex flex-col gap-2 p-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="truncate font-medium">{kpi.label}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-semibold tracking-tight">
          {formatValue(kpi.value)}
        </span>
        {kpi.unit && (
          <span className="text-sm text-muted-foreground">{kpi.unit}</span>
        )}
      </div>
      {change != null && (
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
