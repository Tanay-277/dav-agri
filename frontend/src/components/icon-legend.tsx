"use client"

import { Volume2 } from "lucide-react"

import { CloudIcon } from "@/lib/icons/cloud-icon"
import { ComparisonIcon } from "@/lib/icons/comparison-icon"
import { ForecastIcon } from "@/lib/icons/forecast-icon"
import { HumidityIcon } from "@/lib/icons/humidity-icon"
import { RainIcon } from "@/lib/icons/rain-icon"
import { RainProbabilityIcon } from "@/lib/icons/rain-probability-icon"
import { RecommendationIcon } from "@/lib/icons/recommendation-icon"
import { SunnyIcon } from "@/lib/icons/sunny-icon"
import { TemperatureIcon } from "@/lib/icons/temperature-icon"
import { TrendDownIcon } from "@/lib/icons/trend-down-icon"
import { TrendUpIcon } from "@/lib/icons/trend-up-icon"
import { WarningIcon } from "@/lib/icons/warning-icon"
import { WindIcon } from "@/lib/icons/wind-icon"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface IconLegendProps {
  simpleMode: boolean
  onToggleSimple: () => void
  onReadAloud: () => void
  isSpeaking: boolean
  activeIcon?: string | null
}

const ICONS = [
  { id: "rain", icon: RainIcon, label: "Rainfall" },
  { id: "temperature", icon: TemperatureIcon, label: "Temperature" },
  { id: "humidity", icon: HumidityIcon, label: "Humidity" },
  { id: "cloud", icon: CloudIcon, label: "Cloud cover" },
  { id: "sunny", icon: SunnyIcon, label: "Sunny" },
  { id: "wind", icon: WindIcon, label: "Wind" },
  { id: "probability", icon: RainProbabilityIcon, label: "Rain probability" },
  { id: "trend-up", icon: TrendUpIcon, label: "Increasing" },
  { id: "trend-down", icon: TrendDownIcon, label: "Decreasing" },
  { id: "warning", icon: WarningIcon, label: "Warning" },
  { id: "comparison", icon: ComparisonIcon, label: "Comparison" },
  { id: "forecast", icon: ForecastIcon, label: "Forecast" },
  { id: "recommendation", icon: RecommendationIcon, label: "Recommendation" },
]

export function IconLegend({ simpleMode, onToggleSimple, onReadAloud, isSpeaking, activeIcon }: IconLegendProps) {
  return (
    <Card className="p-3">
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap items-center gap-1.5">
          {ICONS.map(({ id, icon: Icon, label }) => {
            const isActive = activeIcon === id
            return (
              <span
                key={id}
                className={`flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs transition-colors ${
                  isActive ? "border-primary bg-primary/10" : "border-border"
                }`}
                title={label}
              >
                <Icon className={`size-3.5 ${isActive ? "text-primary" : "text-foreground"}`} aria-hidden="true" />
                {!simpleMode && <span className="hidden sm:inline">{label}</span>}
              </span>
            )
          })}
        </div>
        <div className="ml-auto flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onReadAloud}
            aria-label={isSpeaking ? "Stop reading" : "Read dashboard aloud"}
          >
            <Volume2 className={`size-4 ${isSpeaking ? "animate-pulse text-primary" : ""}`} />
          </Button>
          <Button
            variant={simpleMode ? "default" : "outline"}
            size="sm"
            onClick={onToggleSimple}
            aria-pressed={simpleMode}
          >
            {simpleMode ? "Standard View" : "Simple View"}
          </Button>
        </div>
      </div>
    </Card>
  )
}
