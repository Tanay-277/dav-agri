import { renderHook, act } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { useTaskLogger } from "@/hooks/use-task-logger"

function getLastBody(fetchSpy: ReturnType<typeof vi.fn>) {
  const calls = fetchSpy.mock.calls ?? []
  const last = calls[calls.length - 1]
  expect(last).toBeDefined()
  return JSON.parse(last![1].body as string)
}

describe("useTaskLogger", () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it("logs voice_used false when voice is not used (any condition)", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)

    for (const condition of ["conventional", "voice-only", "voice-icons", "voice-story"]) {
      const { result } = renderHook(() => useTaskLogger(condition, "user-1"))

      act(() => result.current.startTask("t1"))
      act(() => result.current.completeTask("t1", true))

      await act(async () => {
        await Promise.resolve()
      })

      const body = getLastBody(fetchSpy)
      expect(body.voice_used).toBe(false)
      expect(body.condition).toBe(condition)
      expect(body.task_id).toBe("t1")
      expect(body.completed).toBe(true)
      expect(typeof body.duration_ms).toBe("number")
    }
  })

  it("logs voice_used true when markVoiceUsed is called (any condition)", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)

    for (const condition of ["conventional", "voice-only", "voice-icons", "voice-story"]) {
      const { result } = renderHook(() => useTaskLogger(condition, "user-1"))

      act(() => result.current.startTask("t1"))
      act(() => result.current.markVoiceUsed())
      act(() => result.current.completeTask("t1", true))

      await act(async () => {
        await Promise.resolve()
      })

      const body = getLastBody(fetchSpy)
      expect(body.voice_used).toBe(true)
      expect(body.condition).toBe(condition)
    }
  })

  it("resets voice_used when starting a new task", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)

    const { result } = renderHook(() => useTaskLogger("voice-icons", "user-2"))

    act(() => result.current.startTask("t1"))
    act(() => result.current.markVoiceUsed())
    act(() => result.current.completeTask("t1", true))

    await act(async () => {
      await Promise.resolve()
    })

    const firstBody = getLastBody(fetchSpy)
    expect(firstBody.voice_used).toBe(true)
    expect(firstBody.task_id).toBe("t1")

    act(() => result.current.startTask("t2"))
    act(() => result.current.completeTask("t2", true))

    await act(async () => {
      await Promise.resolve()
    })

    const secondBody = getLastBody(fetchSpy)
    expect(secondBody.voice_used).toBe(false)
    expect(secondBody.task_id).toBe("t2")
  })

  it("records error when task is interrupted", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)

    const { result } = renderHook(() => useTaskLogger("conventional", "user-3"))

    act(() => result.current.startTask("t1"))
    act(() => result.current.completeTask("t1", false, "interrupted"))

    await act(async () => {
      await Promise.resolve()
    })

    const body = getLastBody(fetchSpy)
    expect(body.completed).toBe(false)
    expect(body.error).toBe("interrupted")
    expect(body.voice_used).toBe(false)
  })

  it("does not log when completing a different task than the active one", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)

    const { result } = renderHook(() => useTaskLogger("voice-only", "user-4"))

    act(() => result.current.startTask("t1"))
    act(() => result.current.completeTask("t2", true))

    await act(async () => {
      await Promise.resolve()
    })

    expect(fetchSpy).not.toHaveBeenCalled()
  })

  it("logs duration correctly", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)

    const { result } = renderHook(() => useTaskLogger("voice-story", "user-5"))

    act(() => result.current.startTask("t1"))

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    act(() => result.current.completeTask("t1", true))

    await act(async () => {
      await Promise.resolve()
    })

    const body = getLastBody(fetchSpy)
    expect(body.duration_ms).toBeGreaterThanOrEqual(100)
  })

  it("payload contains all required fields for research analysis", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)

    const { result } = renderHook(() => useTaskLogger("voice-icons", "user-6"))

    act(() => result.current.startTask("t1"))
    act(() => result.current.markVoiceUsed())
    act(() => result.current.completeTask("t1", true))

    await act(async () => {
      await Promise.resolve()
    })

    const body = getLastBody(fetchSpy)
    expect(body.task_id).toBe("t1")
    expect(body.condition).toBe("voice-icons")
    expect(body.user_id).toBe("user-6")
    expect(body.completed).toBe(true)
    expect(typeof body.duration_ms).toBe("number")
    expect(body.voice_used).toBe(true)
  })
})
