# Implementation Plan: Icon-Based Visual Storytelling Language

## Goal

Create the icon system and integration points defined in `1787113505674-icon-storytelling-language.md`, so the dashboard can communicate weather/agriculture concepts with shape-first, accessibility-safe visuals.

## Non-Negotiables

- Shape-first, color-second semantics.
- Every icon must have `aria-label` text equivalent.
- Animations must respect `prefers-reduced-motion: reduce`.
- No icon should rely on color alone to convey meaning.

## Task 1: Add icon SVG components

Create the following files in `frontend/src/lib/icons/`:

- `temperature-icon.tsx`
- `rain-icon.tsx`
- `rain-probability-icon.tsx`
- `wind-icon.tsx`
- `humidity-icon.tsx`
- `cloud-icon.tsx`
- `sunny-icon.tsx`
- `warning-icon.tsx`
- `trend-up-icon.tsx`
- `trend-down-icon.tsx`
- `comparison-icon.tsx`
- `forecast-icon.tsx`
- `recommendation-icon.tsx`

Requirements per file:
- Export a single React component accepting `SVGProps<SVGSVGElement>` and `className`.
- Use 24×24 viewBox, stroke-based, `strokeWidth="2"`, `strokeLinecap="round"`, `strokeLinejoin="round"`.
- Include an `aria-label` on the root `<svg>` with a plain-text equivalent.

## Task 2: Create `IconAnchor` component

Create `frontend/src/components/icon-anchor.tsx`.

Requirements:
- Accept `icon`, `label`, `active`, `className`, and optional `animate`.
- Render the icon with a wrapper that supports:
  - `active` highlight state (ring or background)
  - optional pulse animation when `animate` is true
- Use `prefers-reduced-motion` media query to disable animation.
- Expose `aria-live="polite"` so screen readers announce state changes.

## Task 3: Create animation utilities

Create `frontend/src/lib/animations.ts`.

Export:
- `useReducedMotion()` → returns `boolean` from `window.matchMedia`.
- `pulseKeyframes` / CSS module or Tailwind-compatible animation classes.
- `transitionPreset(durationMs)` → returns Tailwind transition classes.

Rule: if `useReducedMotion()` is true, return `animation-none` and `transition-none`.

## Task 4: Update `IconLegend`

Edit `frontend/src/components/icon-legend.tsx`.

Requirements:
- Replace hardcoded lucide icons with the new `lib/icons/*` components.
- Add `aria-label` to each icon pill.
- Ensure simple mode enlarges icons and preserves meaning without color.

## Task 5: Integrate icons into KPI cards

Edit `frontend/src/components/kpi-card.tsx`.

Requirements:
- Map each KPI `label` to the corresponding icon component.
- Render icon to the left of the value with `aria-hidden="true"` on the decorative icon, but keep `aria-label` on the wrapper.
- In simple mode, show only the icon and value; hide change/unit text.

## Task 6: Integrate icons into story/insights panels

Edit `frontend/src/components/story-panel.tsx` and `frontend/src/components/insights-panel.tsx`.

Requirements:
- When an insight or story sentence mentions a metric, prepend the matching icon.
- Do not animate icons by default; only animate on explicit TTS sync event.

## Task 7: Add TTS-synced highlighting

Edit `frontend/src/pages/dashboard-page.tsx` and `frontend/src/hooks/use-voice-output.ts`.

Requirements:
- Add a `currentWord` or `currentSentence` state to `useVoiceOutput`.
- Expose an `onBoundary` callback from `SpeechSynthesisUtterance` (`onboundary` event).
- Pass the active icon id to `IconLegend` / `IconAnchor` so the matching icon highlights while its phrase is spoken.

## Task 8: Accessibility pass

- Run `npm run build` and verify no TypeScript errors.
- Verify every icon wrapper has `aria-label`.
- Verify no information is conveyed by color alone (test with grayscale if needed).
- Verify animations are disabled when `prefers-reduced-motion: reduce`.

## Validation

1. `npm run build` succeeds.
2. Backend tests still pass (`pytest tests/test_api.py -v`).
3. Manual: open dashboard, confirm icons render in KPI cards, story panel, and icon legend.
4. Manual: enable voice-story condition, click read aloud, confirm icon highlights during narration.
