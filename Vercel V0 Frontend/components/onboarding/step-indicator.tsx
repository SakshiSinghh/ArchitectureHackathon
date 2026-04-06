"use client"

import { cn } from "@/lib/utils"
import { useOnboarding } from "@/lib/onboarding-context"
import { Check } from "lucide-react"

const steps = [
  { id: 1, label: "Project" },
  { id: 2, label: "Location" },
  { id: 3, label: "Intent" },
  { id: 4, label: "Orientation" },
  { id: 5, label: "Constraints" },
  { id: 6, label: "Priorities" },
  { id: 7, label: "Summary" },
]

export function StepIndicator() {
  const { step } = useOnboarding()

  return (
    <div className="flex items-center gap-2">
      {steps.map((s, index) => (
        <div key={s.id} className="flex items-center gap-2">
          <div
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-all duration-300",
              step > s.id
                ? "bg-primary text-primary-foreground"
                : step === s.id
                  ? "bg-primary text-primary-foreground ring-4 ring-primary/20"
                  : "bg-muted text-muted-foreground"
            )}
          >
            {step > s.id ? <Check className="h-4 w-4" /> : s.id}
          </div>
          {index < steps.length - 1 && (
            <div
              className={cn(
                "hidden h-0.5 w-6 transition-colors duration-300 sm:block",
                step > s.id ? "bg-primary" : "bg-muted"
              )}
            />
          )}
        </div>
      ))}
    </div>
  )
}
