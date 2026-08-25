import { useCallback, useEffect, useRef, useState } from "react"

import type { VoiceResponsePolicy } from "@/lib/voice-intents"
import { DEFAULT_POLICY } from "@/lib/voice-intents"

export interface VoiceOutputState {
  isSpeaking: boolean
  isSupported: boolean
  voices: SpeechSynthesisVoice[]
  selectedVoice: SpeechSynthesisVoice | null
  setVoice: (voice: SpeechSynthesisVoice) => void
  speak: (text: string, lang?: string, policy?: Partial<VoiceResponsePolicy>) => void
  cancel: () => void
  pause: () => void
  resume: () => void
  queue: string[]
  currentWordIndex: number
  onWordBoundary: (index: number) => void
}

export function useVoiceOutput(onWordBoundary?: (index: number) => void) {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null)
  const [queue, setQueue] = useState<string[]>([])
  const [currentWordIndex, setCurrentWordIndex] = useState(-1)
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)
  const policyRef = useRef<VoiceResponsePolicy>(DEFAULT_POLICY)

  useEffect(() => {
    if (typeof window === "undefined" || !window.speechSynthesis) return

    const loadVoices = () => {
      const v = window.speechSynthesis!.getVoices()
      setVoices(v)
      setSelectedVoice((prev) => prev || v[0] || null)
    }

    loadVoices()
    window.speechSynthesis.onvoiceschanged = loadVoices
    return () => {
      window.speechSynthesis!.onvoiceschanged = null
    }
  }, [])

  const speak = useCallback(
    (text: string, lang?: string, policy?: Partial<VoiceResponsePolicy>) => {
      if (!window.speechSynthesis) return
      const merged = { ...policyRef.current, ...policy }
      policyRef.current = merged

      const sentences = text.split(/(?<=[.!?])\s+/).filter(Boolean)
      const trimmed = sentences.slice(0, merged.maxSentences).join(" ")
      const words = trimmed.split(/\s+/)
      const finalText = words.length > merged.maxWords ? words.slice(0, merged.maxWords).join(" ") + "..." : trimmed

      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(finalText)
      if (lang) utterance.lang = lang
      if (selectedVoice) utterance.voice = selectedVoice
      utterance.rate = merged.rate

      utterance.onboundary = (event: SpeechSynthesisEvent) => {
        if (event.name === "word") {
          const idx = finalText.slice(0, event.charIndex).split(/\s+/).length - 1
          setCurrentWordIndex(idx)
          onWordBoundary?.(idx)
        }
      }

      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => {
        setIsSpeaking(false)
        setCurrentWordIndex(-1)
        setQueue((prev) => prev.slice(1))
      }
      utterance.onerror = () => {
        setIsSpeaking(false)
        setCurrentWordIndex(-1)
      }
      utteranceRef.current = utterance
      window.speechSynthesis.speak(utterance)
    },
    [selectedVoice, onWordBoundary]
  )

  const enqueue = useCallback(
    (text: string, lang?: string) => {
      setQueue((prev) => [...prev, text])
      if (!isSpeaking) {
        speak(text, lang)
      }
    },
    [isSpeaking, speak]
  )

  const cancel = useCallback(() => {
    window.speechSynthesis?.cancel()
    setIsSpeaking(false)
    setQueue([])
    setCurrentWordIndex(-1)
  }, [])

  const pause = useCallback(() => {
    window.speechSynthesis?.pause()
  }, [])

  const resume = useCallback(() => {
    window.speechSynthesis?.resume()
  }, [])

  return {
    isSpeaking,
    isSupported: typeof window !== "undefined" && Boolean(window.speechSynthesis),
    voices,
    selectedVoice,
    setVoice: setSelectedVoice,
    speak,
    enqueue,
    cancel,
    pause,
    resume,
    queue,
    currentWordIndex,
    onWordBoundary: onWordBoundary ?? (() => {}),
  }
}
