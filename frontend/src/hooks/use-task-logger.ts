import { useCallback, useEffect, useRef } from "react"

const TASKS = [
  { id: "weather_outlook", label: "Weather outlook (3-day forecast)" },
  { id: "rainfall_trend", label: "Rainfall trend analysis (30 days)" },
  { id: "soil_moisture", label: "Soil moisture status" },
  { id: "sowing_suitability", label: "Sowing/harvesting suitability" },
  { id: "yield_insight", label: "Crop-specific yield insight" },
  { id: "voice_exploration", label: "Voice-driven data exploration" },
  { id: "story_review", label: "Automated story review" },
  { id: "recommendation_review", label: "Recommendation review" },
]

export interface TaskRecord {
  task_id: string
  condition: string
  user_id?: string
  completed: boolean
  duration_ms: number
  voice_used: boolean
  error?: string
}

export function useTaskLogger(condition: string, user_id?: string) {
  const activeTaskRef = useRef<{ task_id: string; start: number } | null>(null)
  const voiceUsedRef = useRef(false)

  const startTask = useCallback((task_id: string) => {
    activeTaskRef.current = { task_id, start: Date.now() }
    voiceUsedRef.current = false
  }, [])

  const markVoiceUsed = useCallback(() => {
    voiceUsedRef.current = true
  }, [])

  const completeTask = useCallback(
    (task_id: string, completed: boolean = true, error?: string) => {
      if (!activeTaskRef.current || activeTaskRef.current.task_id !== task_id) return
      const duration_ms = Date.now() - activeTaskRef.current.start
      const record: TaskRecord = {
        task_id,
        condition,
        user_id,
        completed,
        duration_ms,
        voice_used: voiceUsedRef.current,
        error,
      }
      fetch("/api/v1/research/task-log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(record),
      }).catch(() => {})
      activeTaskRef.current = null
      voiceUsedRef.current = false
    },
    [condition, user_id]
  )

  useEffect(() => {
    return () => {
      if (activeTaskRef.current) {
        completeTask(activeTaskRef.current.task_id, false, "interrupted")
      }
    }
  }, [completeTask])

  return { TASKS, startTask, completeTask, markVoiceUsed }
}
