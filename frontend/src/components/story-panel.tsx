import { Bot, Lightbulb, RefreshCw } from "lucide-react"

import type { Story } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function StoryPanel({
  story,
  onRegenerate,
  regenerating,
}: {
  story: Story | null
  onRegenerate: () => void
  regenerating?: boolean
}) {
  return (
    <Card className="flex flex-col">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-2">
          <Bot className="size-4 text-primary" />
          <CardTitle>Data Story</CardTitle>
        </div>
        <button
          type="button"
          onClick={onRegenerate}
          disabled={regenerating}
          className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:opacity-50"
        >
          <RefreshCw
            className={`size-3.5 ${regenerating ? "animate-spin" : ""}`}
          />
          {story?.source === "ai" ? "Regenerate (AI)" : "Regenerate"}
        </button>
      </CardHeader>
      <CardContent className="flex flex-col gap-4 pt-0">
        {story ? (
          <>
            <p className="leading-relaxed text-foreground/90">{story.story}</p>
            {story.recommendations.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
                  Recommended actions
                </p>
                <ul className="flex flex-col gap-1.5">
                  {story.recommendations.map((rec, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-sm text-foreground/80"
                    >
                      <span className="mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full bg-primary/10">
                        <Lightbulb className="size-3 text-primary" />
                      </span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        ) : (
          <p className="text-sm text-muted-foreground">
            Select a data range to generate a narrative story.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
