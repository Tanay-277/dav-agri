import { type ReactNode } from "react"

interface WeatherCardProps {
  icon: ReactNode
  label: string
  value: string | number
  unit?: string
  change?: number | null
  changeLabel?: string | null
  severity?: "info" | "warning" | "critical"
  loading?: boolean
}

export function WeatherCard({
  icon,
  label,
  value,
  unit,
  change,
  changeLabel,
  severity = "info",
  loading = false,
}: WeatherCardProps) {
  const severityStyles = {
    info: "border-border",
    warning: "border-orange-300 bg-orange-50/50",
    critical: "border-red-300 bg-red-50/50",
  }

  if (loading) {
    return (
      <div className={`rounded-2xl border ${severityStyles[severity]} p-4 animate-pulse`}>
        <div className="flex items-center gap-3">
          <div className="size-12 rounded-full bg-muted" />
          <div className="flex-1">
            <div className="h-4 w-20 rounded bg-muted" />
            <div className="mt-2 h-8 w-16 rounded bg-muted" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`rounded-2xl border ${severityStyles[severity]} p-4 transition-colors`}>
      <div className="flex items-center gap-3">
        <div className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-2xl font-semibold tracking-tight">
            {value}
            {unit && <span className="text-base font-normal text-muted-foreground">{unit}</span>}
          </p>
          {change !== null && change !== undefined && (
            <div className="mt-1 flex items-center gap-1">
              <span
                className={`text-xs font-medium ${change >= 0 ? "text-green-600" : "text-red-600"}`}
              >
                {change >= 0 ? "+" : ""}
                {change}
              </span>
              {changeLabel && <span className="text-xs text-muted-foreground">{changeLabel}</span>}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
