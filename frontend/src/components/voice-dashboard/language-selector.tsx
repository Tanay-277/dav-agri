"use client"

import { useState } from "react"
import { Check, Languages, Type, Minus, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

const LANGUAGES = [
  { code: "en", label: "English", bcp47: "en-US" },
  { code: "hi", label: "हिंदी", bcp47: "hi-IN" },
  { code: "ta", label: "தமிழ்", bcp47: "ta-IN" },
  { code: "te", label: "తెలుగు", bcp47: "te-IN" },
  { code: "kn", label: "ಕನ್ನಡ", bcp47: "kn-IN" },
  { code: "mr", label: "मराठी", bcp47: "mr-IN" },
  { code: "bn", label: "বাংলা", bcp47: "bn-IN" },
]

interface LanguageSelectorProps {
  selected: string
  onSelect: (code: string, bcp47: string) => void
}

export function LanguageSelector({ selected, onSelect }: LanguageSelectorProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="icon-sm"
        onClick={() => setOpen(!open)}
        aria-label="Select language"
        aria-expanded={open}
      >
        <Languages className="size-5" aria-hidden="true" />
        <span className="sr-only">Language</span>
      </Button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} aria-hidden="true" />
          <Card className="absolute right-0 top-full z-50 mt-2 w-48 p-1">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  onSelect(lang.code, lang.bcp47)
                  setOpen(false)
                }}
                className={`flex w-full items-center justify-between rounded-lg px-3 py-3 text-sm transition-colors hover:bg-muted ${
                  selected === lang.code ? "bg-muted font-medium" : ""
                }`}
              >
                <span>{lang.label}</span>
                {selected === lang.code && <Check className="size-4 text-primary" aria-hidden="true" />}
              </button>
            ))}
          </Card>
        </>
      )}
    </div>
  )
}

interface AccessibilityControlsProps {
  fontSize: "normal" | "large" | "xlarge"
  onFontSizeChange: (size: "normal" | "large" | "xlarge") => void
  highContrast: boolean
  onHighContrastChange: (enabled: boolean) => void
}

export function AccessibilityControls({
  fontSize,
  onFontSizeChange,
  highContrast,
  onHighContrastChange,
}: AccessibilityControlsProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="icon-sm"
        onClick={() => setOpen(!open)}
        aria-label="Accessibility options"
        aria-expanded={open}
      >
        <Type className="size-5" aria-hidden="true" />
        <span className="sr-only">Accessibility</span>
      </Button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} aria-hidden="true" />
          <Card className="absolute right-0 top-full z-50 mt-2 w-64 p-4">
            <div className="mb-3">
              <p className="mb-2 text-sm font-medium">Text Size</p>
              <div className="flex items-center gap-2">
                <Button
                  variant={fontSize === "normal" ? "default" : "outline"}
                  size="icon-sm"
                  onClick={() => onFontSizeChange("normal")}
                  aria-label="Normal text size"
                >
                  <Minus className="size-4" aria-hidden="true" />
                </Button>
                <span className="flex-1 text-center text-sm capitalize">{fontSize}</span>
                <Button
                  variant={fontSize === "xlarge" ? "default" : "outline"}
                  size="icon-sm"
                  onClick={() => onFontSizeChange("xlarge")}
                  aria-label="Extra large text"
                >
                  <Plus className="size-4" aria-hidden="true" />
                </Button>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">High Contrast</span>
              <button
                role="switch"
                aria-checked={highContrast}
                onClick={() => onHighContrastChange(!highContrast)}
                className={`relative inline-flex h-8 w-14 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${
                  highContrast ? "bg-primary" : "bg-muted"
                }`}
              >
                <span
                  className={`inline-block h-6 w-6 rounded-full bg-background shadow-lg transition-transform duration-200 ease-in-out ${
                    highContrast ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          </Card>
        </>
      )}
    </div>
  )
}
