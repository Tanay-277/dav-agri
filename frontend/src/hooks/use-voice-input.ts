import { useCallback, useEffect, useRef, useState } from "react"

import { resolveContext } from "@/lib/voice-intents"
import type { ConversationContext, ParsedIntent } from "@/lib/voice-intents"
import type { SpeechRecognitionEvent, SpeechRecognitionErrorEvent, SpeechRecognition, WindowWithSpeech } from "@/types/speech"

const SpeechRecognition = (() => {
  if (typeof window === "undefined") return null
  const w = window as WindowWithSpeech
  return w.SpeechRecognition || w.webkitSpeechRecognition || null
})()

type RecognitionInstance = {
  continuous: boolean
  interimResults: boolean
  lang: string
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
  onend: (() => void) | null
  start(): void
  stop(): void
  abort(): void
}

export interface VoiceInputState {
  isListening: boolean
  transcript: string
  interimTranscript: string
  error: string | null
  isSupported: boolean
}

export interface ConfirmationState {
  pending: boolean
  message: string
  onConfirm: () => void
  onCancel: () => void
}

export interface ClarificationState {
  pending: boolean
  message: string
  options: string[]
  onSelect: (option: string) => void
}

export function useVoiceInput(
  onSpeak?: (text: string) => void,
) {
  const recognitionRef = useRef<RecognitionInstance | null>(null)
  const [state, setState] = useState<VoiceInputState>({
    isListening: false,
    transcript: "",
    interimTranscript: "",
    error: null,
    isSupported: Boolean(SpeechRecognition),
  })

  const [context, setContext] = useState<ConversationContext>({})
  const [confirmation, setConfirmation] = useState<ConfirmationState>({ pending: false, message: "", onConfirm: () => {}, onCancel: () => {} })
  const [clarification, setClarification] = useState<ClarificationState>({ pending: false, message: "", options: [], onSelect: () => {} })
  const silenceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const clearSilenceTimer = useCallback(() => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current)
      silenceTimerRef.current = null
    }
  }, [])

  const startSilenceTimer = useCallback(() => {
    clearSilenceTimer()
    silenceTimerRef.current = setTimeout(() => {
      setState((prev) => ({ ...prev, isListening: false }))
      recognitionRef.current?.stop()
    }, 8000)
  }, [clearSilenceTimer])

  useEffect(() => {
    if (!SpeechRecognition) return
    const recognition = new SpeechRecognition() as RecognitionInstance
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = "en-US"

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      startSilenceTimer()
      let final = ""
      let interim = ""
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          final += t
        } else {
          interim += t
        }
      }
      setState((prev) => ({
        ...prev,
        transcript: final || prev.transcript,
        interimTranscript: interim,
      }))
    }

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      clearSilenceTimer()
      if (event.error === "no-speech") {
        setState((prev) => ({ ...prev, isListening: false }))
        return
      }
      if (event.error === "aborted") {
        return
      }
      setState((prev) => ({
        ...prev,
        isListening: false,
        error: event.error === "not-allowed"
          ? "Microphone access denied."
          : `Speech error: ${event.error}`,
      }))
    }

    recognition.onend = () => {
      clearSilenceTimer()
      setState((prev) => ({ ...prev, isListening: false }))
    }

    recognitionRef.current = recognition
    return () => {
      clearSilenceTimer()
      recognition.abort()
    }
  }, [startSilenceTimer, clearSilenceTimer])

  const start = useCallback((lang?: string) => {
    if (!recognitionRef.current) return
    if (lang) recognitionRef.current.lang = lang
    try {
      recognitionRef.current.start()
      setState((prev) => ({ ...prev, isListening: true, error: null, transcript: "", interimTranscript: "" }))
      startSilenceTimer()
    } catch {
      // already started
    }
  }, [startSilenceTimer])

  const stop = useCallback(() => {
    clearSilenceTimer()
    if (!recognitionRef.current) return
    recognitionRef.current.stop()
    setState((prev) => ({ ...prev, isListening: false }))
  }, [clearSilenceTimer])

  const handleIntent = useCallback(
    (intent: ParsedIntent) => {
      if (intent.action === "confirm") {
        confirmation.onConfirm()
        setConfirmation({ pending: false, message: "", onConfirm: () => {}, onCancel: () => {} })
        return
      }
      if (intent.action === "cancel") {
        confirmation.onCancel()
        setConfirmation({ pending: false, message: "", onConfirm: () => {}, onCancel: () => {} })
        return
      }
      if (intent.needsConfirmation && intent.action === "filter") {
        const msg = intent.entities.crop && intent.entities.state
          ? `Show ${intent.entities.crop} in ${intent.entities.state}?`
          : intent.entities.crop
            ? `Show ${intent.entities.crop} for all states?`
            : "Apply this filter?"
        setConfirmation({
          pending: true,
          message: msg,
          onConfirm: () => {
            onSpeak?.(`Showing ${intent.entities.crop || "all crops"} in ${intent.entities.state || "all states"}.`)
            setContext((prev) => ({ ...prev, ...intent.entities }))
          },
          onCancel: () => {
            onSpeak?.("Filter cancelled.")
          },
        })
        return
      }
      if (intent.clarificationOptions && intent.clarificationOptions.length > 0 && intent.confidence < 0.7) {
        setClarification({
          pending: true,
          message: "What do you want to know?",
          options: intent.clarificationOptions,
          onSelect: (option: string) => {
            onSpeak?.(`Showing ${option}.`)
            setContext((prev) => ({ ...prev, lastMetric: option }))
          },
        })
        return
      }
      setContext((prev) => resolveContext(intent.entities, prev))
    },
    [confirmation, onSpeak]
  )

  const resetContext = useCallback(() => {
    setContext({})
  }, [])

  return {
    ...state,
    context,
    confirmation,
    clarification,
    start,
    stop,
    handleIntent,
    resetContext,
  }
}
