import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { SectionCard } from "@/components/voice-dashboard/section-card"
import { Sun } from "lucide-react"

describe("SectionCard", () => {
  it("renders title and children", () => {
    render(<SectionCard title="Weather" icon={<Sun data-testid="icon" />}>Content here</SectionCard>)
    expect(screen.getByText("Weather")).toBeDefined()
    expect(screen.getByText("Content here")).toBeDefined()
  })

  it("renders loading skeleton when loading", () => {
    render(<SectionCard title="Weather" loading>Content</SectionCard>)
    expect(screen.queryByText("Content")).toBeNull()
  })

  it("renders error state", () => {
    render(<SectionCard title="Weather" error="Failed to load">Content</SectionCard>)
    expect(screen.getByText("Failed to load")).toBeDefined()
  })

  it("renders empty state", () => {
    render(<SectionCard title="Weather" empty={<p>No data</p>} />)
    expect(screen.getByText("No data")).toBeDefined()
  })
})
