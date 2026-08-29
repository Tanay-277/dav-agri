"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { HelpCircle, Mic, MicOff, Volume2, VolumeX, ChevronDown } from "lucide-react"

import { useVoiceOutput } from "@/hooks/use-voice-output"
import { parseVoiceIntent, type ParsedIntent } from "@/lib/voice-intents"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { VoiceConfirmation } from "@/components/voice-confirmation"
import { VoiceClarification } from "@/components/voice-clarification"
import { VoiceHelpModal } from "@/components/voice-help-modal"

const LANGUAGES = [
  { code: "en-US", label: "English" },
  { code: "hi-IN", label: "Hindi" },
  { code: "ta-IN", label: "Tamil" },
  { code: "te-IN", label: "Telugu" },
  { code: "kn-IN", label: "Kannada" },
  { code: "mr-IN", label: "Marathi" },
  { code: "bn-IN", label: "Bengali" },
]

interface VoiceControlsProps {
  onIntent: (intent: ParsedIntent) => void
  transcript: string
  interimTranscript: string
  isListening: boolean
  error: string | null
  isSupported: boolean
  start: (lang?: string) => void
  stop: () => void
  confirmation: { pending: boolean; message: string; onConfirm: () => void; onCancel: () => void }
  clarification: { pending: boolean; message: string; options: string[]; onSelect: (option: string) => void }
  onLanguageChange?: (lang: string) => void
}

export function VoiceControls({
  onIntent,
  transcript,
  interimTranscript,
  isListening,
  error,
  isSupported,
  start,
  stop,
  confirmation,
  clarification,
  onLanguageChange,
}: VoiceControlsProps) {
  const voiceOutput = useVoiceOutput()
  const [lang, setLang] = useState("en-US")
  const [showLang, setShowLang] = useState(false)
  const [showHelp, setShowHelp] = useState(false)
  const lastTranscriptRef = useRef("")

  useEffect(() => {
    if (transcript && transcript !== lastTranscriptRef.current) {
      lastTranscriptRef.current = transcript
      const intent = parseVoiceIntent(transcript)
      onIntent(intent)
    }
  }, [transcript, onIntent])

  const toggleListen = useCallback(() => {
    if (isListening) {
      stop()
    } else {
      start(lang)
    }
  }, [isListening, start, stop, lang])

  const toggleSpeak = useCallback(() => {
    if (voiceOutput.isSpeaking) {
      voiceOutput.cancel()
    }
  }, [voiceOutput])

  if (!isSupported && !voiceOutput.isSupported) {
    return null
  }

  return (
    <Card className="flex flex-wrap items-center gap-3 p-3">
      <div className="flex items-center gap-2">
        <Button
          variant={isListening ? "destructive" : "default"}
          size="sm"
          onClick={toggleListen}
          aria-label={isListening ? "Stop listening" : "Start voice input"}
          title={isListening ? "Stop listening" : "Start voice input"}
        >
          {isListening ? (
            <MicOff className="size-4" />
          ) : (
            <Mic className="size-4" />
          )}
          {isListening ? "Listening…" : "Voice Input"}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={toggleSpeak}
          disabled={!voiceOutput.isSpeaking}
          aria-label={voiceOutput.isSpeaking ? "Stop narration" : "Narration stopped"}
        >
          {voiceOutput.isSpeaking ? (
            <VolumeX className="size-4" />
          ) : (
            <Volume2 className="size-4" />
          )}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowHelp(true)}
          aria-label="Show voice help"
        >
          <HelpCircle className="size-4" />
        </Button>
      </div>

      <div className="relative">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowLang((v) => !v)}
          aria-label="Select language"
        >
          {LANGUAGES.find((l) => l.code === lang)?.label ?? "English"}
          <ChevronDown className="ml-1 size-3" />
        </Button>
        {showLang && (
          <div className="absolute top-full left-0 z-10 mt-1 rounded-lg border bg-background shadow-lg">
            {LANGUAGES.map((l) => (
              <button
                key={l.code}
                onClick={() => {
                  setLang(l.code)
                  setShowLang(false)
                  onLanguageChange?.(l.code)
                }}
                className={`block w-full px-3 py-1.5 text-left text-sm hover:bg-muted ${
                  lang === l.code ? "font-medium text-primary" : ""
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {(transcript || interimTranscript) && (
        <span className="text-xs text-muted-foreground italic">
          &ldquo;{transcript}
          {interimTranscript && <span className="opacity-70">{interimTranscript}</span>}&rdquo;
        </span>
      )}

      {error && (
        <span className="text-xs text-destructive">{error}</span>
      )}

      {confirmation.pending && (
        <VoiceConfirmation
          message={confirmation.message}
          onConfirm={confirmation.onConfirm}
          onCancel={confirmation.onCancel}
        />
      )}

      {clarification.pending && (
        <VoiceClarification
          message={clarification.message}
          options={clarification.options}
          onSelect={clarification.onSelect}
        />
      )}

      {showHelp && <VoiceHelpModal onClose={() => setShowHelp(false)} />}
    </Card>
  )
}
