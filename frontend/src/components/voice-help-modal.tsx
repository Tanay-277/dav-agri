"use client"

import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

const COMMANDS = [
  { category: "Filters", examples: ["Show wheat in Punjab", "Filter by Coimbatore", "From 2023-01-01 to 2023-06-01", "Reset filters"] },
  { category: "Weather", examples: ["Will it rain tomorrow?", "How hot is it today?", "Temperature trend", "Is rainfall increasing?"] },
  { category: "Soil & Yield", examples: ["Soil moisture status", "How is wheat doing?", "Why yield dropped?", "Compare wheat with rice"] },
  { category: "Actions", examples: ["What should I do?", "Read aloud", "Simple mode", "Help"] },
  { category: "Control", examples: ["Stop", "Pause", "Resume", "Undo"] },
]

interface VoiceHelpModalProps {
  onClose: () => void
}

export function VoiceHelpModal({ onClose }: VoiceHelpModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Voice Commands</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="size-4" />
          </Button>
        </div>
        <div className="space-y-4">
          {COMMANDS.map((group) => (
            <div key={group.category}>
              <h3 className="mb-2 text-sm font-medium text-primary">{group.category}</h3>
              <ul className="space-y-1">
                {group.examples.map((ex) => (
                  <li key={ex} className="text-sm text-muted-foreground">
                    &ldquo;{ex}&rdquo;
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <p className="mt-4 text-xs text-muted-foreground">
          Tip: Speak naturally. You can mix languages. Say &ldquo;help&rdquo; anytime to see this list.
        </p>
      </Card>
    </div>
  )
}
