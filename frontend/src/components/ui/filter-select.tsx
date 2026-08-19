import { Select } from "@base-ui/react/select"
import { Check, ChevronDown, X } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export interface SelectOption {
  value: string
  label: string
}

interface FilterSelectProps {
  label?: string
  value: string | null
  onChange: (value: string | null) => void
  options: SelectOption[]
  placeholder?: string
  clearable?: boolean
  className?: string
}

export function FilterSelect({
  label,
  value,
  onChange,
  options,
  placeholder = "All",
  clearable = true,
  className,
}: FilterSelectProps) {
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      {label && (
        <label className="text-xs font-medium text-muted-foreground">
          {label}
        </label>
      )}
      <Select.Root
        value={value as never}
        onValueChange={(next) => onChange(next as unknown as string | null)}
      >
        <div className="relative">
          <Select.Trigger
            className={cn(
              "flex h-9 w-full items-center justify-between gap-2 rounded-xl border border-input bg-background px-3 text-sm outline-none",
              "transition-colors hover:bg-muted/40 focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/30",
              "dark:bg-transparent"
            )}
          >
            <Select.Value
              className={cn(
                "truncate",
                value == null && "text-muted-foreground"
              )}
            >
              {(selectedValue) =>
                options.find((o) => o.value === (selectedValue as string))
                  ?.label ?? placeholder
              }
            </Select.Value>
            {clearable && value != null ? (
              <Button
                variant="ghost"
                size="icon-xs"
                type="button"
                aria-label="Clear selection"
                className="shrink-0 text-muted-foreground"
                onClick={(event) => {
                  event.stopPropagation()
                  onChange(null)
                }}
              >
                <X />
              </Button>
            ) : (
              <Select.Icon className="shrink-0 text-muted-foreground">
                <ChevronDown />
              </Select.Icon>
            )}
          </Select.Trigger>
        </div>
        <Select.Portal>
          <Select.Positioner
            side="bottom"
            align="start"
            sideOffset={6}
            className="z-50"
          >
            <Select.Popup className="min-w-[var(--anchor-width)] overflow-hidden rounded-xl border border-border bg-popover text-popover-foreground shadow-lg">
              <Select.List className="max-h-72 overflow-y-auto p-1">
                {options.map((option) => (
                  <Select.Item
                    key={option.value}
                    value={option.value as never}
                    className={cn(
                      "flex cursor-pointer items-center justify-between rounded-lg px-2.5 py-1.5 text-sm outline-none",
                      "select-none data-highlighted:bg-accent data-[selected]:font-medium"
                    )}
                  >
                    <span>{option.label}</span>
                    <Check className="size-4 shrink-0 text-primary opacity-0 data-[selected]:opacity-100" />
                  </Select.Item>
                ))}
              </Select.List>
            </Select.Popup>
          </Select.Positioner>
        </Select.Portal>
      </Select.Root>
    </div>
  )
}
