"use client"

import { useEffect, useRef, useState } from "react"
import { Mic, MicOff, Loader2, AlertCircle } from "lucide-react"

import { Card } from "@/components/ui/card"

interface VoiceAreaProps {
  isListening: boolean
  isProcessing: boolean
  transcript: string
  interimTranscript: string
  error: string | null
  isSupported: boolean
  onStart: () => void
  onStop: () => void
  language: string
}

export function VoiceArea({
  isListening,
  isProcessing,
  transcript,
  interimTranscript,
  error,
  isSupported,
  onStart,
  onStop,
  language,
}: VoiceAreaProps) {
  const [pulseAnimation, setPulseAnimation] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (isListening) {
      setPulseAnimation(true)
      intervalRef.current = setInterval(() => {
        setPulseAnimation((prev) => !prev)
      }, 1000)
    } else {
      setPulseAnimation(false)
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isListening])

  if (!isSupported) {
    return (
      <Card className="p-6 text-center">
        <AlertCircle className="mx-auto mb-3 size-12 text-destructive" aria-hidden="true" />
        <p className="text-lg font-medium">Voice Not Supported</p>
        <p className="mt-2 text-sm text-muted-foreground">
          Your browser does not support speech recognition. Please use text input or try a different browser.
        </p>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <div className="flex flex-col items-center gap-4">
        <button
          onClick={isListening ? onStop : onStart}
          disabled={isProcessing}
          aria-label={isListening ? "Stop listening" : "Start listening"}
          className={`relative flex h-24 w-24 items-center justify-center rounded-full transition-all duration-300 ${
            isListening
              ? "bg-destructive/10 text-destructive"
              : "bg-primary/10 text-primary hover:bg-primary/20"
          } ${isProcessing ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
        >
          {isProcessing ? (
            <Loader2 className="size-10 animate-spin" aria-hidden="true" />
          ) : isListening ? (
            <MicOff className="size-10" aria-hidden="true" />
          ) : (
            <Mic className="size-10" aria-hidden="true" />
          )}
          {isListening && (
            <span
              className={`absolute inset-0 rounded-full border-4 border-destructive/30 ${
                pulseAnimation ? "animate-ping opacity-75" : "opacity-0"
              }`}
              aria-hidden="true"
            />
          )}
        </button>
        <div className="text-center">
          <p className="text-lg font-medium">
            {isListening ? "Listening..." : isProcessing ? "Processing..." : "Tap to speak"}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {isListening
              ? `Speaking in ${language}`
              : isProcessing
                ? "Please wait"
                : "Ask about weather, rain, or crops"}
          </p>
        </div>
        {(transcript || interimTranscript) && (
          <div className="w-full rounded-xl bg-muted/50 p-4 text-center">
            <p className="text-sm text-muted-foreground">You said:</p>
            <p className="mt-1 text-lg font-medium">
              {transcript}
              {interimTranscript && <span className="text-muted-foreground">{interimTranscript}</span>}
            </p>
          </div>
        )}
        {error && (
          <div className="flex items-center gap-2 rounded-xl bg-destructive/10 p-4 text-destructive">
            <AlertCircle className="size-5 shrink-0" aria-hidden="true" />
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}
      </div>
    </Card>
  )
}
