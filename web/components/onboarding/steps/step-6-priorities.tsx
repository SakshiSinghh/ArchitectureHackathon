"use client"

import { useState } from "react"
import { useOnboarding } from "@/lib/onboarding-context"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import {
  OnboardingCard,
  OnboardingCardHeader,
  OnboardingCardTitle,
  OnboardingCardDescription,
  OnboardingCardContent,
  OnboardingCardFooter,
} from "../onboarding-card"
import { ArrowRight, ArrowLeft, SlidersHorizontal, Sun, Zap, DollarSign, Sparkles } from "lucide-react"

const priorityOptions = [
  {
    key: "daylight" as const,
    label: "Daylight",
    description: "Natural light optimization",
    icon: Sun,
  },
  {
    key: "energyEfficiency" as const,
    label: "Energy Efficiency",
    description: "Reduce consumption",
    icon: Zap,
  },
  {
    key: "cost" as const,
    label: "Cost",
    description: "Budget optimization",
    icon: DollarSign,
  },
  {
    key: "aesthetics" as const,
    label: "Aesthetics",
    description: "Visual appeal",
    icon: Sparkles,
  },
]

export function Step6Priorities() {
  const { projectData, updateProjectData, setStep } = useOnboarding()
  const [priorities, setPriorities] = useState(projectData.priorities)

  const handleSliderChange = (key: keyof typeof priorities, value: number[]) => {
    setPriorities((prev) => ({ ...prev, [key]: value[0] }))
  }

  const handleContinue = () => {
    updateProjectData({ priorities })
    setStep(7)
  }

  const handleBack = () => {
    updateProjectData({ priorities })
    setStep(5)
  }

  return (
    <OnboardingCard className="max-w-xl">
      <OnboardingCardHeader>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
          <SlidersHorizontal className="h-7 w-7 text-primary" />
        </div>
        <OnboardingCardTitle>Set your priorities</OnboardingCardTitle>
        <OnboardingCardDescription>
          Balance what matters most for your project
        </OnboardingCardDescription>
      </OnboardingCardHeader>
      <OnboardingCardContent>
        <div className="space-y-6">
          {priorityOptions.map((option) => {
            const Icon = option.icon
            return (
              <div key={option.key} className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div>
                      <div className="text-sm font-medium">{option.label}</div>
                      <div className="text-xs text-muted-foreground">
                        {option.description}
                      </div>
                    </div>
                  </div>
                  <span className="text-sm font-semibold tabular-nums">
                    {priorities[option.key]}%
                  </span>
                </div>
                <Slider
                  value={[priorities[option.key]]}
                  onValueChange={(value) => handleSliderChange(option.key, value)}
                  max={100}
                  step={5}
                  className="w-full"
                />
              </div>
            )
          })}
        </div>
      </OnboardingCardContent>
      <OnboardingCardFooter>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleBack} size="lg">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Button onClick={handleContinue} size="lg" className="gap-2">
            Continue
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </OnboardingCardFooter>
    </OnboardingCard>
  )
}
