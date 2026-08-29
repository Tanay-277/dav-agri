import { type ReactNode } from "react"
import { TrendingUp, CloudRain } from "lucide-react"
import { Card } from "@/components/ui/card"
import { SectionCard } from "@/components/voice-dashboard/section-card"

interface ForecastItem {
  day: string
  date: string
  high: number
  low: number
  condition: string
  rainProbability: number
}

interface ForecastAreaProps {
  forecast: ForecastItem[]
  loading: boolean
  error: string | null
  location?: string
}

const conditionIcons: Record<string, ReactNode> = {
  sunny: <span className="text-2xl" aria-hidden="true">☀️</span>,
  cloudy: <span className="text-2xl" aria-hidden="true">☁️</span>,
  rainy: <span className="text-2xl" aria-hidden="true">🌧️</span>,
  snowy: <span className="text-2xl" aria-hidden="true">❄️</span>,
}

export function ForecastArea({ forecast, loading, error, location }: ForecastAreaProps) {
  if (!forecast.length && !loading && !error) {
    return (
      <SectionCard title="7-Day Forecast" icon={<TrendingUp className="size-5" aria-hidden="true" />}>
        <p className="text-sm text-muted-foreground">Ask about the forecast to see it here.</p>
      </SectionCard>
    )
  }

  return (
    <SectionCard
      title={location ? `${location} Forecast` : "7-Day Forecast"}
      icon={<TrendingUp className="size-5" aria-hidden="true" />}
      loading={loading}
      error={error}
    >
      {forecast.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
          {forecast.map((day) => (
            <Card key={day.date} className="p-3 text-center">
              <p className="text-sm font-medium">{day.day}</p>
              <p className="text-xs text-muted-foreground">{day.date}</p>
              <div className="my-2 flex justify-center">
                {conditionIcons[day.condition] || <CloudRain className="size-5" aria-hidden="true" />}
              </div>
              <p className="text-lg font-semibold">{day.high}°</p>
              <p className="text-sm text-muted-foreground">{day.low}°</p>
              <div className="mt-2 flex items-center justify-center gap-1 text-xs text-blue-600">
                <CloudRain className="size-3" aria-hidden="true" />
                <span>{day.rainProbability}%</span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </SectionCard>
  )
}
