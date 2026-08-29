import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { FeedbackArea } from "@/components/voice-dashboard/feedback-area"

describe("FeedbackArea", () => {
  it("renders error message", () => {
    render(<FeedbackArea type="error" message="Something went wrong" />)
    expect(screen.getByText("Something went wrong")).toBeDefined()
  })

  it("renders details when provided", () => {
    render(<FeedbackArea type="info" message="Update available" details="Version 2.0" />)
    expect(screen.getByText("Update available")).toBeDefined()
    expect(screen.getByText("Version 2.0")).toBeDefined()
  })

  it("calls onDismiss when close button clicked", () => {
    const onDismiss = vi.fn()
    render(<FeedbackArea type="success" message="Done" onDismiss={onDismiss} />)
    fireEvent.click(screen.getByLabelText("Dismiss"))
    expect(onDismiss).toHaveBeenCalled()
  })

  it("has alert role for accessibility", () => {
    render(<FeedbackArea type="warning" message="Warning" />)
    expect(screen.getByRole("alert")).toBeDefined()
  })
})
