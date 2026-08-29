import { ErrorBoundary } from "@/components/error-boundary"
import { DashboardPage } from "@/pages/dashboard-page"

export function App() {
  return (
    <ErrorBoundary>
      <DashboardPage />
    </ErrorBoundary>
  )
}

export default App
