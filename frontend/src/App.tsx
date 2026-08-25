import { ErrorBoundary } from "@/components/error-boundary"
import { VoiceDashboard } from "@/components/voice-dashboard/voice-dashboard"

export function App() {
  return (
    <ErrorBoundary>
      <VoiceDashboard />
    </ErrorBoundary>
  )
}

export default App
