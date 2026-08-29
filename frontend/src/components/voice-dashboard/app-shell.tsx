import { type ReactNode } from "react"

interface AppShellProps {
  header?: ReactNode
  main: ReactNode
  footer?: ReactNode
  languageSelector?: ReactNode
  accessibilityControls?: ReactNode
}

export function AppShell({
  header,
  main,
  footer,
  languageSelector,
  accessibilityControls,
}: AppShellProps) {
  return (
    <div className="flex min-h-svh flex-col bg-background">
      {header && (
        <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/10">
                <svg
                  className="size-6 text-primary"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                  <line x1="12" x2="12" y1="19" y2="22" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-semibold tracking-tight">AgriStory</h1>
                <p className="text-xs text-muted-foreground">Voice Assistant</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {languageSelector}
              {accessibilityControls}
            </div>
          </div>
        </header>
      )}
      <main className="flex-1">{main}</main>
      {footer && <footer className="border-t border-border py-4">{footer}</footer>}
    </div>
  )
}
