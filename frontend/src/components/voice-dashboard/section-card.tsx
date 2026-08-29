import { type ReactNode } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface SectionCardProps {
  title: string
  icon?: ReactNode
  children?: ReactNode
  loading?: boolean
  error?: string | null
  empty?: ReactNode
  className?: string
}

export function SectionCard({
  title,
  icon,
  children,
  loading = false,
  error = null,
  empty,
  className = "",
}: SectionCardProps) {
  if (error) {
    return (
      <Card className={`border-destructive/30 bg-destructive/5 ${className}`}>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            {icon}
            <CardTitle className="text-base">{title}</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-destructive">{error}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          {icon}
          <CardTitle className="text-base">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-3">
            <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
            <div className="h-4 w-1/2 animate-pulse rounded bg-muted" />
            <div className="h-4 w-2/3 animate-pulse rounded bg-muted" />
          </div>
        ) : empty && !children ? (
          empty
        ) : (
          children
        )}
      </CardContent>
    </Card>
  )
}
