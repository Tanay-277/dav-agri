import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface ConditionSwitcherProps {
  condition: string
  onConditionChange: (condition: string) => void
}

const CONDITIONS = [
  { value: "conventional", label: "Conventional", description: "Charts + filters only" },
  { value: "voice-only", label: "Voice Only", description: "Voice in/out, no icons/story" },
  { value: "voice-icons", label: "Voice + Icons", description: "Voice + icon legend" },
  { value: "voice-story", label: "Voice + Icons + Story", description: "Full MVRS condition" },
]

export function ConditionSwitcher({ condition, onConditionChange }: ConditionSwitcherProps) {
  return (
    <Card className="p-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium text-muted-foreground">Research condition:</span>
        {CONDITIONS.map((c) => (
          <Button
            key={c.value}
            variant={condition === c.value ? "default" : "outline"}
            size="sm"
            onClick={() => onConditionChange(c.value)}
            title={c.description}
          >
            {c.label}
          </Button>
        ))}
      </div>
    </Card>
  )
}
