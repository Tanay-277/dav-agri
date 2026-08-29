"use client"

import { useEffect, useRef } from "react"
import { X, AlertCircle, Info, CheckCircle, Volume2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useVoiceOutput } from "@/hooks/use-voice-output"

export type FeedbackType = "error" | "info" | "success" | "warning"

interface FeedbackAreaProps {
  type: FeedbackType
  message: string
  details?: string
  onDismiss?: () => void
  autoSpeak?: boolean
}

const feedbackConfig = {
  error: {
    icon: <AlertCircle className="size-5 text-destructive" aria-hidden="true" />,
    bg: "bg-destructive/10 border-destructive/30",
    titleColor: "text-destructive",
  },
  warning: {
    icon: <AlertCircle className="size-5 text-orange-600" aria-hidden="true" />,
    bg: "bg-orange-50 border-orange-300",
    titleColor: "text-orange-900",
  },
  info: {
    icon: <Info className="size-5 text-blue-600" aria-hidden="true" />,
    bg: "bg-blue-50 border-blue-300",
    titleColor: "text-blue-900",
  },
  success: {
    icon: <CheckCircle className="size-5 text-green-600" aria-hidden="true" />,
    bg: "bg-green-50 border-green-300",
    titleColor: "text-green-900",
  },
}

export function FeedbackArea({ type, message, details, onDismiss, autoSpeak = false }: FeedbackAreaProps) {
  const config = feedbackConfig[type]
  const voiceOutput = useVoiceOutput()
  const hasSpokenRef = useRef(false)

  useEffect(() => {
    if (autoSpeak && message && !hasSpokenRef.current) {
      hasSpokenRef.current = true
      voiceOutput.speak(message)
    }
  }, [autoSpeak, message, voiceOutput])

  return (
    <Card className={`border ${config.bg}`} role="alert" aria-live="polite">
      <div className="flex items-start gap-3 p-4">
        <div className="mt-0.5">{config.icon}</div>
        <div className="flex-1">
          <p className={`text-sm font-medium ${config.titleColor}`}>{message}</p>
          {details && <p className="mt-1 text-sm text-muted-foreground">{details}</p>}
        </div>
        <div className="flex items-center gap-1">
          {autoSpeak && (
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={() => voiceOutput.speak(message)}
              aria-label="Repeat message"
            >
              <Volume2 className="size-4" aria-hidden="true" />
            </Button>
          )}
          {onDismiss && (
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={onDismiss}
              aria-label="Dismiss"
            >
              <X className="size-4" aria-hidden="true" />
            </Button>
          )}
        </div>
      </div>
    </Card>
  )
}
