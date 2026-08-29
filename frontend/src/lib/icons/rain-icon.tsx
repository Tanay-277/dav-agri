import type { SVGProps } from "react"

export function RainIcon({ className, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props} aria-label="Rain cloud with droplets">
      <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
      <path d="M8 19v2" />
      <path d="M12 19v2" />
      <path d="M16 19v2" />
    </svg>
  )
}
