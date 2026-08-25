"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface SurveyModalProps {
  condition: string
  onComplete: (responses: {
    comprehension_score: number
    trust_score: number
    sus_score: number
    feedback: string
  }) => void
  onSkip: () => void
}

const COMPREHENSION_QUESTIONS = [
  {
    id: "q1",
    question: "According to the dashboard, what is the main weather condition expected tomorrow?",
    options: ["Rain", "Sunny", "Cloudy", "I don't know"],
    correct: 0,
  },
  {
    id: "q2",
    question: "Is soil moisture currently sufficient for planting?",
    options: ["Yes", "No", "I don't know"],
    correct: 1,
  },
  {
    id: "q3",
    question: "What is the primary recommendation for the selected crop?",
    options: ["Irrigate", "Harvest", "Wait", "I don't know"],
    correct: 2,
  },
]

const TRUST_ITEMS = [
  "I trust the information provided by the system.",
  "I would rely on this system for farming decisions.",
  "The system's explanations are clear and understandable.",
  "I feel confident using this system.",
]

const SUS_ITEMS = [
  "I would like to use this system frequently.",
  "I found the system unnecessarily complex.",
  "I think the system is easy to use.",
  "I would need technical support to use this system.",
  "I found the various functions in this system were well integrated.",
  "I thought there was too much inconsistency in this system.",
  "I would imagine that most people would learn to use this system very quickly.",
  "I found the system very cumbersome to use.",
  "I felt very confident using the system.",
  "I needed to learn a lot of things before I could get going with this system.",
]

function LikertScale({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex gap-2">
      {[1, 2, 3, 4, 5].map((n) => (
        <Button
          key={n}
          variant={value === n ? "default" : "outline"}
          size="sm"
          onClick={() => onChange(n)}
          aria-label={`Rating ${n} out of 5`}
        >
          {n}
        </Button>
      ))}
    </div>
  )
}

export function SurveyModal({ condition, onComplete, onSkip }: SurveyModalProps) {
  const [step, setStep] = useState<"comprehension" | "trust" | "sus" | "feedback">("comprehension")
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [trustRatings, setTrustRatings] = useState<number[]>(Array(4).fill(0))
  const [susRatings, setSusRatings] = useState<number[]>(Array(10).fill(0))
  const [feedback, setFeedback] = useState("")

  const handleAnswer = (qid: string, optionIndex: number) => {
    setAnswers((prev) => ({ ...prev, [qid]: optionIndex }))
  }

  const comprehensionScore = COMPREHENSION_QUESTIONS.reduce((sum, q) => {
    return sum + (answers[q.id] === q.correct ? 1 : 0)
  }, 0)

  const canProceed = step === "comprehension"
    ? COMPREHENSION_QUESTIONS.every((q) => answers[q.id] !== undefined)
    : step === "trust"
      ? trustRatings.every((r) => r > 0)
      : step === "sus"
        ? susRatings.every((r) => r > 0)
        : true

  const handleNext = () => {
    if (step === "comprehension") setStep("trust")
    else if (step === "trust") setStep("sus")
    else if (step === "sus") setStep("feedback")
    else if (step === "feedback") {
      const susSum = susRatings.reduce((a, b) => a + b, 0)
      const susScore = Math.round(((susSum - 10) / 40) * 100)
      onComplete({
        comprehension_score: comprehensionScore,
        trust_score: Math.round(trustRatings.reduce((a, b) => a + b, 0) / trustRatings.length),
        sus_score: susScore,
        feedback,
      })
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold">Research Survey</h2>
          <p className="text-xs text-muted-foreground">Condition: {condition}</p>
        </div>

        {step === "comprehension" && (
          <div className="space-y-4">
            <p className="text-sm font-medium">Please answer the following questions based on the dashboard you just used:</p>
            {COMPREHENSION_QUESTIONS.map((q) => (
              <div key={q.id} className="space-y-2">
                <p className="text-sm">{q.question}</p>
                <div className="flex flex-wrap gap-2">
                  {q.options.map((opt, idx) => (
                    <Button
                      key={idx}
                      variant={answers[q.id] === idx ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleAnswer(q.id, idx)}
                    >
                      {opt}
                    </Button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {step === "trust" && (
          <div className="space-y-4">
            <p className="text-sm font-medium">Please rate your agreement with the following statements (1 = Strongly disagree, 5 = Strongly agree):</p>
            {TRUST_ITEMS.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <p className="text-sm">{item}</p>
                <LikertScale value={trustRatings[idx]} onChange={(v) => setTrustRatings((prev) => { const next = [...prev]; next[idx] = v; return next })} />
              </div>
            ))}
          </div>
        )}

        {step === "sus" && (
          <div className="space-y-4">
            <p className="text-sm font-medium">Please rate your agreement with the following statements (1 = Strongly disagree, 5 = Strongly agree):</p>
            {SUS_ITEMS.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <p className="text-sm">{item}</p>
                <LikertScale value={susRatings[idx]} onChange={(v) => setSusRatings((prev) => { const next = [...prev]; next[idx] = v; return next })} />
              </div>
            ))}
          </div>
        )}

        {step === "feedback" && (
          <div className="space-y-3">
            <p className="text-sm font-medium">Any additional comments or feedback?</p>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Optional feedback..."
              className="h-32 w-full rounded-lg border border-input bg-background p-3 text-sm"
            />
          </div>
        )}

        <div className="mt-6 flex justify-between">
          <Button variant="ghost" onClick={onSkip}>Skip survey</Button>
          <Button onClick={handleNext} disabled={!canProceed}>
            {step === "feedback" ? "Submit" : "Next"}
          </Button>
        </div>
      </Card>
    </div>
  )
}
