import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { WeatherCard } from "@/components/voice-dashboard/weather-card"
import { Sun } from "lucide-react"

describe("WeatherCard", () => {
  it("renders label and value", () => {
    render(<WeatherCard icon={<Sun data-testid="icon" />} label="Temperature" value={28} unit="°C" />)
    expect(screen.getByText("Temperature")).toBeDefined()
    expect(screen.getByText("28")).toBeDefined()
    expect(screen.getByText("°C")).toBeDefined()
  })

  it("shows loading state", () => {
    render(<WeatherCard icon={<Sun data-testid="icon" />} label="Temperature" value={0} loading />)
    expect(screen.queryByText("Temperature")).toBeNull()
  })

  it("displays change when provided", () => {
    render(<WeatherCard icon={<Sun data-testid="icon" />} label="Feels Like" value={31} change={3} changeLabel="above" />)
    expect(screen.getByText("+3")).toBeDefined()
    expect(screen.getByText("above")).toBeDefined()
  })

  it("applies warning styling for warning severity", () => {
    render(<WeatherCard icon={<Sun data-testid="icon" />} label="Humidity" value={85} severity="warning" />)
    const card = screen.getByText("Humidity").closest('[class*="rounded-2xl"]')
    expect(card?.className).toContain("border-orange-300")
  })
})
