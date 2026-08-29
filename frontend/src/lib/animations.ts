"use client"

import { useEffect, useState } from "react"

export function useReducedMotion() {
  const [reduced, setReduced] = useState(false)

  useEffect(() => {
    if (typeof window === "undefined") return
    const mql = window.matchMedia("(prefers-reduced-motion: reduce)")
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setReduced(mql.matches)
    const handler = (e: MediaQueryListEvent) => setReduced(e.matches)
    mql.addEventListener("change", handler)
    return () => mql.removeEventListener("change", handler)
  }, [])

  return reduced
}

export function transitionPreset(durationMs: number) {
  const reduced = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches
  if (reduced) return "transition-none"
  return `transition-all duration-${durationMs} ease-in-out`
}
