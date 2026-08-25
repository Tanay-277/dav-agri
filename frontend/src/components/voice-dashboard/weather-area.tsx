import { type ReactNode } from "react"
import { Sun, Cloud, CloudRain, CloudSnow, Wind, Droplets, Eye } from "lucide-react"
import { WeatherCard } from "@/components/voice-dashboard/weather-card"
import { SectionCard } from "@/components/voice-dashboard/section-card"

interface WeatherData {
  temperature: number
  feelsLike: number
  humidity: number
  condition: string
  windSpeed: number
  visibility: number
  icon?: string
}

interface WeatherAreaProps {
  weather: WeatherData | null
  loading: boolean
  error: string | null
  location?: string
}

const conditionIcons: Record<string, ReactNode> = {
  sunny: <Sun className="size-6" aria-hidden="true" />,
  cloudy: <Cloud className="size-6" aria-hidden="true" />,
  rainy: <CloudRain className="size-6" aria-hidden="true" />,
  snowy: <CloudSnow className="size-6" aria-hidden="true" />,
}

export function WeatherArea({ weather, loading, error, location }: WeatherAreaProps) {
  if (!weather && !loading && !error) {
    return (
      <SectionCard title="Current Weather" icon={<Sun className="size-5" aria-hidden="true" />}>
        <p className="text-sm text-muted-foreground">Ask about the current weather to see it here.</p>
      </SectionCard>
    )
  }

  return (
    <SectionCard
      title={location ? `Weather in ${location}` : "Current Weather"}
      icon={<Sun className="size-5" aria-hidden="true" />}
      loading={loading}
      error={error}
    >
      {weather && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <WeatherCard
            icon={conditionIcons[weather.icon || "sunny"] || <Sun className="size-6" aria-hidden="true" />}
            label="Temperature"
            value={weather.temperature}
            unit="°C"
            change={weather.feelsLike - weather.temperature}
            changeLabel="feels like"
          />
          <WeatherCard
            icon={<Droplets className="size-6" aria-hidden="true" />}
            label="Humidity"
            value={weather.humidity}
            unit="%"
          />
          <WeatherCard
            icon={<Wind className="size-6" aria-hidden="true" />}
            label="Wind Speed"
            value={weather.windSpeed}
            unit="km/h"
          />
          <WeatherCard
            icon={<Eye className="size-6" aria-hidden="true" />}
            label="Visibility"
            value={weather.visibility}
            unit="km"
          />
        </div>
      )}
    </SectionCard>
  )
}
