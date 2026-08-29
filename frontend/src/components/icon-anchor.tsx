"use client"

import { cva, type VariantProps } from "class-variance-authority"
import { useReducedMotion } from "@/lib/animations"

const iconAnchorVariants = cva(
  "inline-flex items-center justify-center rounded-lg",
  {
    variants: {
      active: {
        true: "bg-primary/15 ring-2 ring-primary",
        false: "bg-transparent ring-1 ring-transparent",
      },
      size: {
        sm: "size-8",
        md: "size-10",
        lg: "size-12",
      },
    },
    defaultVariants: {
      active: false,
      size: "md",
    },
  }
)

interface IconAnchorProps extends VariantProps<typeof iconAnchorVariants> {
  icon: React.ReactNode
  label: string
  animate?: boolean
  className?: string
}

export function IconAnchor({ icon, label, active, size, animate, className }: IconAnchorProps) {
  const reducedMotion = useReducedMotion()
  const pulse = animate && !reducedMotion ? "animate-pulse" : ""

  return (
    <span
      className={iconAnchorVariants({ active, size, className })}
      aria-live="polite"
      aria-label={label}
      title={label}
    >
      <span className={pulse} aria-hidden="true">
        {icon}
      </span>
    </span>
  )
}
