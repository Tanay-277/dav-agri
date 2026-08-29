import type { SVGProps } from "react"

export function TemperatureIcon({ className, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props} aria-label="Temperature thermometer">
      <path d="M14 4v10.54a4 4 0 1 1-4 0V4" />
      <path d="M12 11v3" />
      <path d="M9 14h6" />
    </svg>
  )
}
