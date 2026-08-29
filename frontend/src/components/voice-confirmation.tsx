"use client"

import { useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useVoiceInput } from "@/hooks/use-voice-input"
import { useVoiceOutput } from "@/hooks/use-voice-output"

interface VoiceConfirmationProps {
  message: string
  onConfirm: () => void
  onCancel: () => void
}

export function VoiceConfirmation({ message, onConfirm, onCancel }: VoiceConfirmationProps) {
  const voiceInput = useVoiceInput()
  const voiceOutput = useVoiceOutput()
  const spokenRef = useRef(false)

  useEffect(() => {
    if (message && !spokenRef.current) {
      spokenRef.current = true
      voiceOutput.speak(`${message} Say yes or no.`)
    }
  }, [message, voiceOutput])

  useEffect(() => {
    if (!voiceInput.transcript) return
    const last = voiceInput.transcript.toLowerCase()
    if (last.includes("yes") || last.includes("yeah") || last.includes("yep")) {
      onConfirm()
    } else if (last.includes("no") || last.includes("nope") || last.includes("cancel")) {
      onCancel()
    }
  }, [voiceInput.transcript, onConfirm, onCancel])

  return (
    <Card className="flex flex-wrap items-center gap-3 p-4">
      <p className="text-sm font-medium">{message}</p>
      <div className="flex gap-2">
        <Button size="sm" onClick={onConfirm}>Yes</Button>
        <Button size="sm" variant="outline" onClick={onCancel}>No</Button>
      </div>
    </Card>
  )
}
