import { ListChecks } from "lucide-react"

import type { Recommendation } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const priorityStyles: Record<string, string> = {
  high: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
  medium:
    "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
  low: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
}

export function RecommendationsPanel({
  recommendations,
}: {
  recommendations: Recommendation[]
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <ListChecks className="size-4 text-primary" />
          <CardTitle>Recommendations</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="max-h-full space-y-2.5 overflow-y-auto">
        {recommendations.length === 0 && (
          <p className="text-sm text-muted-foreground">
            No recommendations available.
          </p>
        )}
        {recommendations.map((rec, i) => (
          <div
            key={`${rec.condition}-${i}`}
            className="flex items-start justify-between gap-3 rounded-xl border border-border bg-muted/40 p-3"
          >
            <p className="text-sm leading-snug text-foreground/85">
              {rec.message}
            </p>
            <span
              className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase ${priorityStyles[rec.priority] ?? priorityStyles.medium}`}
            >
              {rec.priority}
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
