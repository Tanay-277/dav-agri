import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { DashboardPage } from "@/pages/dashboard-page"
import { api } from "@/services/api"

vi.mock("@/components/charts/line-chart", () => ({
  LineChart: () => null,
}))

vi.mock("@/components/charts/bar-chart", () => ({
  BarChart: () => null,
}))

vi.mock("@/components/charts/scatter-chart", () => ({
  ScatterChart: () => null,
}))

vi.mock("@/components/charts/heatmap-chart", () => ({
  HeatmapChart: () => null,
}))

vi.mock("@/components/charts/pie-chart", () => ({
  PieChart: () => null,
}))

vi.mock("@/services/api", () => ({
  api: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

const mockApplyFilters = vi.fn()
const mockResetFilters = vi.fn()
const mockRegenerateStory = vi.fn()
const mockRegenerateInsights = vi.fn()
const mockExportReport = vi.fn()

vi.mock("@/hooks/use-dashboard", () => ({
  useDashboard: () => ({
    filters: {},
    filterOptions: {
      loaded: true,
      crop: ["Wheat", "Rice"],
      state: ["Punjab", "Maharashtra"],
      district: [],
      date_min: "2022-01-01",
      date_max: "2022-12-31",
    },
    dashboard: {
      charts: {
        line: { title: "Trend", labels: ["Jan"], series: [{ name: "Rain", labels: ["Jan"], values: [10] }] },
        bar: { title: "Bar", labels: ["Punjab"], values: [100] },
        scatter: { title: "Scatter", points: [{ x: 10, y: 20 }] },
        heatmap: { title: "Heat", columns: ["rain", "temp"], matrix: [[1, 0]] },
        pie: { title: "Pie", labels: ["Wheat"], values: [50] },
      },
      kpis: [
        { label: "Avg Rainfall", value: 100, unit: "mm", change: 5, change_label: "vs last period" },
      ],
      metadata: { rows: 600 },
    },
    insights: [
      { type: "info", message: "Rainfall is normal", severity: "info", metric: "rainfall" },
    ],
    story: {
      story: "This is a test story.",
      summary: {},
      reasons: [],
      recommendations: [],
      source: "rule",
    },
    recommendations: [
      { condition: "Normal", message: "No action needed", priority: "low" },
    ],
    loading: false,
    storyLoading: false,
    error: null,
    hasFilters: false,
    activeFilterCount: 0,
    applyFilters: mockApplyFilters,
    resetFilters: mockResetFilters,
    regenerateStory: mockRegenerateStory,
    regenerateInsights: mockRegenerateInsights,
    exportReport: mockExportReport,
  }),
}))

vi.mock("@/hooks/use-task-logger", () => ({
  useTaskLogger: () => ({
    TASKS: [
      { id: "t1", label: "Check weather" },
      { id: "t2", label: "Compare crops" },
      { id: "t3", label: "Review insights" },
    ],
    startTask: vi.fn(),
    completeTask: vi.fn(),
    markVoiceUsed: vi.fn(),
  }),
}))

const mockVoiceInput = {
  isListening: false,
  transcript: "",
  interimTranscript: "",
  error: null,
  isSupported: true,
  context: {},
  confirmation: { pending: false, message: "", onConfirm: vi.fn(), onCancel: vi.fn() },
  clarification: { pending: false, message: "", options: [], onSelect: vi.fn() },
  start: vi.fn(),
  stop: vi.fn(),
  handleIntent: vi.fn(),
  resetContext: vi.fn(),
}

vi.mock("@/hooks/use-voice-input", () => ({
  useVoiceInput: () => mockVoiceInput,
}))

vi.mock("@/hooks/use-voice-output", () => ({
  useVoiceOutput: () => ({
    isSpeaking: false,
    isSupported: true,
    voices: [],
    selectedVoice: null,
    setVoice: vi.fn(),
    speak: vi.fn(),
    enqueue: vi.fn(),
    cancel: vi.fn(),
    pause: vi.fn(),
    resume: vi.fn(),
    queue: [],
    currentWordIndex: 0,
    onWordBoundary: vi.fn(),
  }),
}))

describe("DashboardPage voice query integration", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockVoiceInput.transcript = ""
    mockVoiceInput.isListening = false
    mockVoiceInput.interimTranscript = ""
    mockVoiceInput.error = null
    ;(api.post as ReturnType<typeof vi.fn>).mockClear()
    mockApplyFilters.mockClear()
  })

  it("renders the dashboard with real API-driven data", async () => {
    render(<DashboardPage />)
    expect(screen.getByText("AgriStory Dashboard")).toBeDefined()
    expect(screen.getByText("Avg Rainfall")).toBeDefined()
    expect(screen.getByText("Rainfall is normal")).toBeDefined()
  })

  it("voice query service calls backend with transcript and language", async () => {
    ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        structured_query: { intent: "general_query", entities: {}, raw_query: "test", confidence: 0.5 },
        insights: [],
        speech_response: null,
        message: "OK",
      },
    })

    const { rerender } = render(<DashboardPage />)

    const voiceOnlyButton = screen.getByText("Voice Only")
    voiceOnlyButton.click()

    await waitFor(() => {
      expect(screen.getByText("Voice Input")).toBeDefined()
    })

    const micButton = screen.getByLabelText("Start voice input")
    micButton.click()

    mockVoiceInput.transcript = "what is the rainfall"
    rerender(<DashboardPage />)

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        "/voice/query",
        expect.objectContaining({
          query: "what is the rainfall",
          language: "en",
        }),
      )
    })
  })

  it("applies filters returned from backend voice query", async () => {
    ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        structured_query: {
          intent: "rainfall_query",
          entities: { state: "Punjab", crop: "Wheat" },
          raw_query: "rain in punjab",
          confidence: 0.9,
        },
        insights: [],
        speech_response: null,
        message: "Processed",
      },
    })

    const { rerender } = render(<DashboardPage />)

    const voiceOnlyButton = screen.getByText("Voice Only")
    voiceOnlyButton.click()

    await waitFor(() => {
      expect(screen.getByText("Voice Input")).toBeDefined()
    })

    const micButton = screen.getByLabelText("Start voice input")
    micButton.click()

    mockVoiceInput.transcript = "rain in punjab"
    rerender(<DashboardPage />)

    await waitFor(() => {
      expect(mockApplyFilters).toHaveBeenCalledWith({
        crop: "Wheat",
        state: "Punjab",
        district: undefined,
        start_date: undefined,
        end_date: undefined,
      })
    })
  })

  it("shows error message when backend voice query fails", async () => {
    ;(api.post as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error("Network error"),
    )

    const { rerender } = render(<DashboardPage />)

    const voiceOnlyButton = screen.getByText("Voice Only")
    voiceOnlyButton.click()

    await waitFor(() => {
      expect(screen.getByText("Voice Input")).toBeDefined()
    })

    const micButton = screen.getByLabelText("Start voice input")
    micButton.click()

    mockVoiceInput.transcript = "what is the weather"
    rerender(<DashboardPage />)

    await waitFor(() => {
      expect(api.post).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Network error")
    })
  })

  it("sends selected language code to backend", async () => {
    ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        structured_query: { intent: "general_query", entities: {}, raw_query: "test", confidence: 0.5 },
        insights: [],
        speech_response: null,
        message: "OK",
      },
    })

    const { rerender } = render(<DashboardPage />)

    const voiceOnlyButton = screen.getByText("Voice Only")
    voiceOnlyButton.click()

    await waitFor(() => {
      expect(screen.getByText("Voice Input")).toBeDefined()
    })

    const langButton = screen.getByLabelText("Select language")
    langButton.click()

    const hindiOption = await waitFor(() => screen.getByText("Hindi"))
    hindiOption.click()

    const micButton = screen.getByLabelText("Start voice input")
    micButton.click()

    mockVoiceInput.transcript = "what is the weather"
    rerender(<DashboardPage />)

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        "/voice/query",
        expect.objectContaining({
          query: "what is the weather",
          language: "hi",
        }),
      )
    })
  })

  it("shows clarification options when backend requests them", async () => {
    ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        structured_query: {
          intent: "general_query",
          entities: {},
          raw_query: "how is it going",
          confidence: 0.4,
          needs_clarification: true,
          clarification_options: ["Rainfall", "Temperature", "Humidity", "Soil Moisture"],
          ambiguity_reasons: ["No metric specified"],
        },
        insights: [],
        speech_response: null,
        message: "Please provide more details",
      },
    })

    const { rerender } = render(<DashboardPage />)

    const voiceOnlyButton = screen.getByText("Voice Only")
    voiceOnlyButton.click()

    await waitFor(() => {
      expect(screen.getByText("Voice Input")).toBeDefined()
    })

    const micButton = screen.getByLabelText("Start voice input")
    micButton.click()

    mockVoiceInput.transcript = "how is it going"
    rerender(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("No metric specified")).toBeDefined()
    })
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Rainfall" })).toBeDefined()
    })
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Temperature" })).toBeDefined()
    })
    expect(mockApplyFilters).not.toHaveBeenCalled()
  })

  it("applies filters after user selects clarification option", async () => {
    ;(api.post as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        data: {
          structured_query: {
            intent: "general_query",
            entities: {},
            raw_query: "how is it going",
            confidence: 0.4,
            needs_clarification: true,
            clarification_options: ["Rainfall", "Temperature"],
            ambiguity_reasons: ["No metric specified"],
          },
          insights: [],
          speech_response: null,
          message: "Please provide more details",
        },
      })
      .mockResolvedValueOnce({
        data: {
          structured_query: {
            intent: "rainfall_query",
            entities: { state: "Punjab", metric: "rainfall" },
            raw_query: "rainfall",
            confidence: 0.8,
          },
          insights: [],
          speech_response: null,
          message: "Processed",
        },
      })

    const { rerender } = render(<DashboardPage />)

    const voiceOnlyButton = screen.getByText("Voice Only")
    voiceOnlyButton.click()

    await waitFor(() => {
      expect(screen.getByText("Voice Input")).toBeDefined()
    })

    const micButton = screen.getByLabelText("Start voice input")
    micButton.click()

    mockVoiceInput.transcript = "how is it going"
    rerender(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Rainfall" })).toBeDefined()
    })

    const rainfallButton = screen.getByRole("button", { name: "Rainfall" })
    rainfallButton.click()

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledTimes(2)
    })
    await waitFor(() => {
      expect(mockApplyFilters).toHaveBeenCalledWith({
        crop: undefined,
        state: "Punjab",
        district: undefined,
        start_date: undefined,
        end_date: undefined,
      })
    })
  })

  it("shows error when clarification selection fails", async () => {
    ;(api.post as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        data: {
          structured_query: {
            intent: "general_query",
            entities: {},
            raw_query: "how is it going",
            confidence: 0.4,
            needs_clarification: true,
            clarification_options: ["Rainfall"],
            ambiguity_reasons: ["No metric specified"],
          },
          insights: [],
          speech_response: null,
          message: "Please provide more details",
        },
      })
      .mockRejectedValueOnce(new Error("Network error"))

    const { rerender } = render(<DashboardPage />)

    const voiceOnlyButton = screen.getByText("Voice Only")
    voiceOnlyButton.click()

    await waitFor(() => {
      expect(screen.getByText("Voice Input")).toBeDefined()
    })

    const micButton = screen.getByLabelText("Start voice input")
    micButton.click()

    mockVoiceInput.transcript = "how is it going"
    rerender(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Rainfall" })).toBeDefined()
    })

    const rainfallButton = screen.getByRole("button", { name: "Rainfall" })
    rainfallButton.click()

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Network error")
    })
  })

  it("does not show clarification UI when backend returns empty options", async () => {
    ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        structured_query: {
          intent: "general_query",
          entities: {},
          raw_query: "how is it going",
          confidence: 0.4,
          needs_clarification: true,
          clarification_options: [],
          ambiguity_reasons: ["No metric specified"],
        },
        insights: [],
        speech_response: null,
        message: "Please provide more details",
      },
    })

    const { rerender } = render(<DashboardPage />)

    const voiceOnlyButton = screen.getByText("Voice Only")
    voiceOnlyButton.click()

    await waitFor(() => {
      expect(screen.getByText("Voice Input")).toBeDefined()
    })

    const micButton = screen.getByLabelText("Start voice input")
    micButton.click()

    mockVoiceInput.transcript = "how is it going"
    rerender(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Please provide more details")).toBeDefined()
    })
    expect(screen.queryByRole("button", { name: "Rainfall" })).toBeNull()
  })
})
