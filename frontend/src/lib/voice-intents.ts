export interface ParsedIntent {
  action:
    | "filter"
    | "reset"
    | "query"
    | "read_aloud"
    | "stop"
    | "pause"
    | "resume"
    | "simple_mode"
    | "standard_mode"
    | "help"
    | "confirm"
    | "cancel"
    | "undo"
    | "unknown"
  entities: {
    crop?: string
    state?: string
    district?: string
    startDate?: string
    endDate?: string
    metric?: string
    comparison?: string
  }
  raw: string
  confidence: number
  needsConfirmation: boolean
  clarificationOptions?: string[]
}

export interface ConversationContext {
  last_crop?: string
  last_state?: string
  last_district?: string
  last_metric?: string
  last_date_range?: { start?: string; end?: string }
}

export interface VoiceResponsePolicy {
  maxSentences: number
  maxWords: number
  rate: number
  preferComparisons: boolean
  useIcons: boolean
}

export const DEFAULT_POLICY: VoiceResponsePolicy = {
  maxSentences: 3,
  maxWords: 60,
  rate: 0.9,
  preferComparisons: true,
  useIcons: true,
}

const CROPS = [
  "Wheat", "Rice", "Sugarcane", "Cotton", "Maize", "Pulses", "Groundnut", "Soybean",
]

const STATES = [
  "Karnataka", "Maharashtra", "Tamil Nadu", "Punjab", "Gujarat",
  "Andhra Pradesh", "Madhya Pradesh", "Rajasthan",
]

const DISTRICTS: Record<string, string[]> = {
  Karnataka: ["Bangalore", "Mysore", "Belgaum", "Gulbarga", "Shimoga"],
  Maharashtra: ["Pune", "Nagpur", "Nashik", "Aurangabad", "Kolhapur"],
  "Tamil Nadu": ["Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Madras"],
  Punjab: ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
  Gujarat: ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
  "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Kurnool"],
  "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain"],
  Rajasthan: ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
}

const METRICS = [
  "rain", "rainfall", "rain water", "precipitation",
  "temperature", "temp", "heat", "hot", "cold",
  "humidity", "moisture", "soil moisture",
  "yield", "production", "crop",
  "wind", "speed", "forecast", "weather",
]

const COMPARISON_PHRASES = [
  "compare", "comparison", "vs", "versus", "difference", "better", "worse",
]

const HELP_PHRASES = [
  "help", "what can you do", "commands", "options", "how to use",
]

const RESET_PHRASES = [
  "reset", "clear", "remove filters", "show all", "all crops", "all states",
]

const READ_ALOUD_PHRASES = [
  "read aloud", "tell me the story", "read story", "narrate", "speak",
]

const STOP_PHRASES = ["stop", "cancel", "shut up", "quiet"]
const PAUSE_PHRASES = ["pause", "wait", "hold on"]
const RESUME_PHRASES = ["resume", "continue", "go on"]
const SIMPLE_PHRASES = ["simple mode", "simple view", "easy mode"]
const STANDARD_PHRASES = ["standard mode", "normal mode", "full view", "detailed view"]
const CONFIRM_PHRASES = ["yes", "yeah", "yep", "correct", "right", "confirm"]
const CANCEL_PHRASES = ["no", "nope", "wrong", "cancel", "incorrect"]
const UNDO_PHRASES = ["undo", "go back", "revert", "previous"]

function matchToken(tokens: string[], candidates: string[]): string | undefined {
  const lower = tokens.map((t) => t.toLowerCase())
  for (const c of candidates) {
    if (lower.includes(c.toLowerCase())) return c
  }
  return undefined
}

function matchMultiWord(raw: string, candidates: string[]): string | undefined {
  const lower = raw.toLowerCase()
  for (const c of candidates) {
    if (lower.includes(c.toLowerCase())) return c
  }
  return undefined
}

export function parseVoiceIntent(
  transcript: string,
  context: ConversationContext = {}
): ParsedIntent {
  const raw = transcript.trim()
  if (!raw) {
    return { action: "unknown", entities: {}, raw, confidence: 0, needsConfirmation: false }
  }

  const lower = raw.toLowerCase()
  const tokens = raw.split(/\s+/)

  // Detect action keywords
  const isReset = matchMultiWord(lower, RESET_PHRASES)
  const isHelp = matchMultiWord(lower, HELP_PHRASES)
  const isReadAloud = matchMultiWord(lower, READ_ALOUD_PHRASES)
  const isStop = matchMultiWord(lower, STOP_PHRASES)
  const isPause = matchMultiWord(lower, PAUSE_PHRASES)
  const isResume = matchMultiWord(lower, RESUME_PHRASES)
  const isSimple = matchMultiWord(lower, SIMPLE_PHRASES)
  const isStandard = matchMultiWord(lower, STANDARD_PHRASES)
  const isConfirm = matchMultiWord(lower, CONFIRM_PHRASES)
  const isCancel = matchMultiWord(lower, CANCEL_PHRASES)
  const isUndo = matchMultiWord(lower, UNDO_PHRASES)
  const isComparison = matchMultiWord(lower, COMPARISON_PHRASES)

  // Entity extraction
  const crop = matchToken(tokens, CROPS)
  const state = matchToken(tokens, STATES)
  let district: string | undefined
  if (state && DISTRICTS[state]) {
    district = matchToken(tokens, DISTRICTS[state])
  }

  const dateMatch = raw.match(/(\d{4}-\d{2}-\d{2})/g)
  let startDate: string | undefined
  let endDate: string | undefined
  if (dateMatch && dateMatch.length >= 2) {
    startDate = dateMatch[0]
    endDate = dateMatch[1]
  } else if (dateMatch && dateMatch.length === 1) {
    startDate = dateMatch[0]
    endDate = dateMatch[0]
  }

  const metric = matchToken(tokens, METRICS)

  // Context resolution for follow-ups
  const resolvedCrop = crop || context.last_crop
  const resolvedState = state || context.last_state
  const resolvedDistrict = district || context.last_district
  const resolvedMetric = metric || context.last_metric

  // Confidence scoring
  let confidence: number
  let needsConfirmation = false
  let clarificationOptions: string[] = []

  if (isReset) {
    return { action: "reset", entities: {}, raw, confidence: 0.95, needsConfirmation: true, clarificationOptions: [] }
  }
  if (isHelp) {
    return { action: "help", entities: {}, raw, confidence: 0.95, needsConfirmation: false }
  }
  if (isReadAloud) {
    return { action: "read_aloud", entities: {}, raw, confidence: 0.9, needsConfirmation: false }
  }
  if (isStop) {
    return { action: "stop", entities: {}, raw, confidence: 0.9, needsConfirmation: false }
  }
  if (isPause) {
    return { action: "pause", entities: {}, raw, confidence: 0.9, needsConfirmation: false }
  }
  if (isResume) {
    return { action: "resume", entities: {}, raw, confidence: 0.9, needsConfirmation: false }
  }
  if (isSimple) {
    return { action: "simple_mode", entities: {}, raw, confidence: 0.9, needsConfirmation: false }
  }
  if (isStandard) {
    return { action: "standard_mode", entities: {}, raw, confidence: 0.9, needsConfirmation: false }
  }
  if (isUndo) {
    return { action: "undo", entities: {}, raw, confidence: 0.9, needsConfirmation: false }
  }

  // Confirm/cancel only valid if there is a pending action (handled by caller)
  if (isConfirm) {
    return { action: "confirm", entities: {}, raw, confidence: 0.9, needsConfirmation: false }
  }
  if (isCancel) {
    return { action: "cancel", entities: {}, raw, confidence: 0.9, needsConfirmation: false }
  }

  // Query / filter detection
  const hasEntity = resolvedCrop || resolvedState || resolvedDistrict || resolvedMetric || startDate || endDate
  if (!hasEntity && !isComparison) {
    // Could be a vague query like "how is it going?"
    if (lower.includes("how") || lower.includes("what") || lower.includes("is") || lower.includes("should")) {
      return {
        action: "query",
        entities: { metric: resolvedMetric, crop: resolvedCrop, state: resolvedState, district: resolvedDistrict },
        raw,
        confidence: 0.4,
        needsConfirmation: false,
        clarificationOptions: ["rainfall", "temperature", "soil moisture", "yield"],
      }
    }
    return { action: "unknown", entities: {}, raw, confidence: 0.1, needsConfirmation: false }
  }

  // Determine if this is a filter or a query
  if (resolvedCrop || resolvedState || resolvedDistrict || startDate || endDate) {
    confidence = 0.7
    if (!resolvedCrop && !resolvedState && !resolvedDistrict) {
      needsConfirmation = true
      clarificationOptions = METRICS.filter(m => !["forecast", "weather"].includes(m)).slice(0, 4)
    } else if (resolvedCrop && !resolvedState && !resolvedDistrict) {
      // Partial location info
      needsConfirmation = true
      clarificationOptions = [`${resolvedCrop} in all states`, `specify a state`]
    }
    return {
      action: "filter",
      entities: { crop: resolvedCrop, state: resolvedState, district: resolvedDistrict, startDate, endDate, metric: resolvedMetric },
      raw,
      confidence,
      needsConfirmation,
      clarificationOptions,
    }
  }

  if (isComparison) {
    return {
      action: "query",
      entities: { metric: resolvedMetric, crop: resolvedCrop, state: resolvedState, district: resolvedDistrict },
      raw,
      confidence: 0.75,
      needsConfirmation: false,
    }
  }

  return {
    action: "query",
    entities: { metric: resolvedMetric, crop: resolvedCrop, state: resolvedState, district: resolvedDistrict },
    raw,
    confidence: 0.6,
    needsConfirmation: false,
  }
}

export function resolveContext(entities: ParsedIntent["entities"], context: ConversationContext): ConversationContext {
  return {
    last_crop: entities.crop || context.last_crop,
    last_state: entities.state || context.last_state,
    last_district: entities.district || context.last_district,
    last_metric: entities.metric || context.last_metric,
    last_date_range: entities.startDate || entities.endDate ? { start: entities.startDate, end: entities.endDate } : context.last_date_range,
  }
}
