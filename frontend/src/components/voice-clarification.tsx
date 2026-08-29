"use client"

import { useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useVoiceInput } from "@/hooks/use-voice-input"
import { useVoiceOutput } from "@/hooks/use-voice-output"

interface VoiceClarificationProps {
  message: string
  options: string[]
  onSelect: (option: string) => void
}

export function VoiceClarification({ message, options, onSelect }: VoiceClarificationProps) {
  const voiceInput = useVoiceInput()
  const voiceOutput = useVoiceOutput()
  const spokenRef = useRef(false)

  useEffect(() => {
    if (message && !spokenRef.current) {
      spokenRef.current = true
      const optText = options.join(", ")
      voiceOutput.speak(`${message} Say ${optText}.`)
    }
  }, [message, options, voiceOutput])

  useEffect(() => {
    if (!voiceInput.transcript) return
    const last = voiceInput.transcript.toLowerCase()
    const match = options.find((opt) => last.includes(opt.toLowerCase()))
    if (match) {
      onSelect(match)
    }
  }, [voiceInput.transcript, options, onSelect])

  return (
    <Card className="flex flex-wrap items-center gap-3 p-4">
      <p className="text-sm font-medium">{message}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <Button key={opt} size="sm" variant="outline" onClick={() => onSelect(opt)}>
            {opt}
          </Button>
        ))}
      </div>
    </Card>
  )
}
