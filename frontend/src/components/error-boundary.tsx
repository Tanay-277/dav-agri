import { Component, type ReactNode } from "react"

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public state: ErrorBoundaryState = {
    hasError: false,
    error: null,
  }

  public static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: { componentStack: string }) {
    console.error("Unhandled error:", error, errorInfo.componentStack)
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }
      return (
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="flex flex-col items-center gap-3 rounded-2xl border border-destructive/30 bg-destructive/10 p-6 text-center">
            <p className="text-sm font-medium text-destructive">
              Something went wrong.
            </p>
            <p className="text-xs text-muted-foreground">
              {this.state.error?.message ?? "Please refresh the page."}
            </p>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
