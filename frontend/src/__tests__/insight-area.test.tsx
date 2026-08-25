import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { InsightArea } from "@/components/voice-dashboard/insight-area"

describe("InsightArea", () => {
  const insights = [
    { id: "1", type: "crop", message: "Good conditions for wheat", severity: "info" as const, magnitude: 2 },
    { id: "2", type: "weather", message: "Heavy rain expected", severity: "warning" as const, magnitude: -1 },
  ]

  it("renders insights list", () => {
    render(<InsightArea insights={insights} loading={false} error={null} />)
    expect(screen.getByText("Good conditions for wheat")).toBeDefined()
    expect(screen.getByText("Heavy rain expected")).toBeDefined()
  })

  it("shows loading skeleton", () => {
    render(<InsightArea insights={[]} loading={true} error={null} />)
    expect(screen.queryByText("Good conditions for wheat")).toBeNull()
  })

  it("shows error state", () => {
    render(<InsightArea insights={[]} loading={false} error="Failed to load insights" />)
    expect(screen.getByText("Failed to load insights")).toBeDefined()
  })

  it("renders empty prompt when no insights", () => {
    render(<InsightArea insights={[]} loading={false} error={null} />)
    expect(screen.getByText("Ask about crops or weather to see insights.")).toBeDefined()
  })
})
