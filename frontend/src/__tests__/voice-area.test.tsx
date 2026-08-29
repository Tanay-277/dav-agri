import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { VoiceArea } from "@/components/voice-dashboard/voice-area"

describe("VoiceArea", () => {
  const defaultProps = {
    isListening: false,
    isProcessing: false,
    transcript: "",
    interimTranscript: "",
    error: null,
    isSupported: true,
    onStart: vi.fn(),
    onStop: vi.fn(),
    language: "en-US",
  }

  it("renders tap to speak prompt when idle", () => {
    render(<VoiceArea {...defaultProps} />)
    expect(screen.getByText("Tap to speak")).toBeDefined()
  })

  it("shows listening state when active", () => {
    render(<VoiceArea {...defaultProps} isListening={true} />)
    expect(screen.getByText("Listening...")).toBeDefined()
  })

  it("displays transcript when available", () => {
    render(<VoiceArea {...defaultProps} transcript="hello world" />)
    expect(screen.getByText("hello world")).toBeDefined()
  })

  it("displays error message", () => {
    render(<VoiceArea {...defaultProps} error="Microphone access denied" />)
    expect(screen.getByText("Microphone access denied")).toBeDefined()
  })

  it("calls onStart when mic button clicked", () => {
    const onStart = vi.fn()
    render(<VoiceArea {...defaultProps} onStart={onStart} />)
    fireEvent.click(screen.getByLabelText("Start listening"))
    expect(onStart).toHaveBeenCalled()
  })

  it("shows unsupported message when not supported", () => {
    render(<VoiceArea {...defaultProps} isSupported={false} />)
    expect(screen.getByText("Voice Not Supported")).toBeDefined()
  })
})
