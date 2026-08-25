import { useState, useCallback } from "react"

import { Card } from "@/components/ui/card"
import { VoiceArea } from "@/components/voice-dashboard/voice-area"
import { WeatherArea } from "@/components/voice-dashboard/weather-area"
import { ForecastArea } from "@/components/voice-dashboard/forecast-area"
import { InsightArea } from "@/components/voice-dashboard/insight-area"
import { FeedbackArea, type FeedbackType } from "@/components/voice-dashboard/feedback-area"
import { LanguageSelector } from "@/components/voice-dashboard/language-selector"
import { AccessibilityControls } from "@/components/voice-dashboard/language-selector"
import { useVoiceInput } from "@/hooks/use-voice-input"
import type { ParsedIntent } from "@/lib/voice-intents"

interface WeatherData {
  temperature: number
  feelsLike: number
  humidity: number
  condition: string
  windSpeed: number
  visibility: number
  icon?: string
}

interface ForecastItem {
  day: string
  date: string
  high: number
  low: number
  condition: string
  rainProbability: number
}

interface InsightItem {
  id: string
  type: string
  message: string
  severity: "info" | "warning" | "critical"
  magnitude?: number | null
}

export function VoiceDashboard() {
  const [language, setLanguage] = useState("en")
  const [fontSize, setFontSize] = useState<"normal" | "large" | "xlarge">("normal")
  const [highContrast, setHighContrast] = useState(false)
  const [feedback, setFeedback] = useState<{ type: FeedbackType; message: string; details?: string; autoSpeak?: boolean } | null>(null)

  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [forecast, setForecast] = useState<ForecastItem[]>([])
  const [insights, setInsights] = useState<InsightItem[]>([])

  const [weatherLoading, setWeatherLoading] = useState(false)
  const [forecastLoading, setForecastLoading] = useState(false)
  const [insightsLoading, setInsightsLoading] = useState(false)

  const [weatherError, setWeatherError] = useState<string | null>(null)
  const [forecastError, setForecastError] = useState<string | null>(null)
  const [insightsError, setInsightsError] = useState<string | null>(null)

  const handleSpeak = useCallback((text: string) => {
    setFeedback({ type: "info", message: text, autoSpeak: true })
    setTimeout(() => setFeedback(null), 5000)
  }, [])

  const voiceInput = useVoiceInput(handleSpeak)

  const handleIntent = useCallback(
    (intent: ParsedIntent) => {
      voiceInput.handleIntent(intent)

      if (intent.action === "query" || intent.action === "filter") {
        setFeedback(null)

        if (intent.entities.metric?.includes("weather") || intent.raw.toLowerCase().includes("weather")) {
          setWeatherLoading(true)
          setWeatherError(null)
          setTimeout(() => {
            setWeather({
              temperature: 28,
              feelsLike: 31,
              humidity: 65,
              condition: "partly cloudy",
              windSpeed: 12,
              visibility: 8,
              icon: "cloudy",
            })
            setWeatherLoading(false)
            handleSpeak("Current temperature is 28 degrees Celsius.")
          }, 1000)
        }

        if (intent.entities.metric?.includes("forecast") || intent.raw.toLowerCase().includes("forecast")) {
          setForecastLoading(true)
          setForecastError(null)
          setTimeout(() => {
            setForecast([
              { day: "Mon", date: "Aug 24", high: 30, low: 22, condition: "sunny", rainProbability: 0 },
              { day: "Tue", date: "Aug 25", high: 29, low: 21, condition: "cloudy", rainProbability: 20 },
              { day: "Wed", date: "Aug 26", high: 27, low: 20, condition: "rainy", rainProbability: 80 },
              { day: "Thu", date: "Aug 27", high: 28, low: 21, condition: "cloudy", rainProbability: 40 },
              { day: "Fri", date: "Aug 28", high: 31, low: 23, condition: "sunny", rainProbability: 0 },
              { day: "Sat", date: "Aug 29", high: 32, low: 24, condition: "sunny", rainProbability: 0 },
              { day: "Sun", date: "Aug 30", high: 30, low: 22, condition: "cloudy", rainProbability: 15 },
            ])
            setForecastLoading(false)
            handleSpeak("Here is the 7-day forecast.")
          }, 1200)
        }

        if (intent.entities.crop || intent.entities.metric?.includes("crop")) {
          setInsightsLoading(true)
          setInsightsError(null)
          setTimeout(() => {
            setInsights([
              { id: "1", type: "crop", message: "Good conditions for wheat planting this week.", severity: "info", magnitude: 2 },
              { id: "2", type: "weather", message: "Heavy rain expected on Wednesday. Consider early harvesting.", severity: "warning", magnitude: -1 },
              { id: "3", type: "market", message: "Market prices for rice are up 5% this week.", severity: "info", magnitude: 5 },
            ])
            setInsightsLoading(false)
            handleSpeak("I found 3 insights for you.")
          }, 1500)
        }
      }
    },
    [voiceInput, handleSpeak]
  )

  const handleLanguageSelect = useCallback((code: string, bcp47: string) => {
    setLanguage(code)
    voiceInput.start(bcp47)
    handleSpeak(`Language changed to ${code === "en" ? "English" : code}`)
  }, [voiceInput, handleSpeak])

  const handleFontSizeChange = useCallback((size: "normal" | "large" | "xlarge") => {
    setFontSize(size)
  }, [])

  const handleHighContrastChange = useCallback((enabled: boolean) => {
    setHighContrast(enabled)
  }, [])

  return (
    <div className={`min-h-svh bg-background ${highContrast ? "contrast-more" : ""}`}>
      <div className="container mx-auto px-4 py-4 sm:px-6 sm:py-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className={`font-semibold tracking-tight ${fontSize === "normal" ? "text-2xl" : fontSize === "large" ? "text-3xl" : "text-4xl"}`}>
              AgriStory
            </h1>
            <p className={`text-muted-foreground ${fontSize === "normal" ? "text-sm" : "text-base"}`}>
              Voice-First Agricultural Assistant
            </p>
          </div>
          <div className="flex items-center gap-2">
            <LanguageSelector selected={language} onSelect={handleLanguageSelect} />
            <AccessibilityControls
              fontSize={fontSize}
              onFontSizeChange={handleFontSizeChange}
              highContrast={highContrast}
              onHighContrastChange={handleHighContrastChange}
            />
          </div>
        </div>

        {feedback && (
          <div className="mb-4">
            <FeedbackArea
              type={feedback.type}
              message={feedback.message}
              details={feedback.details}
              onDismiss={() => setFeedback(null)}
              autoSpeak={feedback.autoSpeak}
            />
          </div>
        )}

        <div className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <VoiceArea
              isListening={voiceInput.isListening}
              isProcessing={false}
              transcript={voiceInput.transcript}
              interimTranscript={voiceInput.interimTranscript}
              error={voiceInput.error}
              isSupported={voiceInput.isSupported}
              onStart={() => voiceInput.start()}
              onStop={voiceInput.stop}
              language={language}
            />

            <WeatherArea
              weather={weather}
              loading={weatherLoading}
              error={weatherError}
              location="Bangalore"
            />

            <ForecastArea
              forecast={forecast}
              loading={forecastLoading}
              error={forecastError}
              location="Bangalore"
            />
          </div>

          <div className="space-y-4">
            <InsightArea insights={insights} loading={insightsLoading} error={insightsError} />

            <Card className="p-4">
              <h3 className="mb-3 text-sm font-medium text-muted-foreground">Voice Commands</h3>
              <div className="space-y-2">
                {[
                  "What is the weather?",
                  "Show 7-day forecast",
                  "Tell me about wheat",
                  "Rain forecast",
                  "Help",
                ].map((cmd) => (
                  <button
                    key={cmd}
                    onClick={() => {
                      const mockIntent: ParsedIntent = {
                        action: "query",
                        entities: {
                          metric: cmd.toLowerCase().includes("weather") ? "weather" : cmd.toLowerCase().includes("forecast") ? "forecast" : "crop",
                        },
                        raw: cmd,
                        confidence: 1,
                        needsConfirmation: false,
                      }
                      handleIntent(mockIntent)
                    }}
                    className="w-full rounded-xl border border-border p-3 text-left text-sm transition-colors hover:bg-muted"
                  >
                    {cmd}
                  </button>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
