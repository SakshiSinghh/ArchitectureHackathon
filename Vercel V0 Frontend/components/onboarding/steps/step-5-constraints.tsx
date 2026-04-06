"use client"

import { useState } from "react"
import { useOnboarding } from "@/lib/onboarding-context"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import {
  OnboardingCard,
  OnboardingCardHeader,
  OnboardingCardTitle,
  OnboardingCardDescription,
  OnboardingCardContent,
  OnboardingCardFooter,
} from "../onboarding-card"
import { ArrowRight, ArrowLeft, Lock, RotateCcw, Layers, ArrowUpFromLine } from "lucide-react"

const constraintOptions = [
  {
    key: "lockOrientation" as const,
    label: "Lock Orientation",
    description: "Keep the building facing fixed",
    icon: RotateCcw,
  },
  {
    key: "lockFacade" as const,
    label: "Lock Facade",
    description: "Preserve the exterior design",
    icon: Layers,
  },
  {
    key: "heightRestriction" as const,
    label: "Height Restriction",
    description: "Apply local zoning limits",
    icon: ArrowUpFromLine,
  },
]

export function Step5Constraints() {
  const { projectData, updateProjectData, setStep } = useOnboarding()
  const [constraints, setConstraints] = useState(projectData.constraints)

  const handleToggle = (key: keyof typeof constraints) => {
    setConstraints((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const handleContinue = () => {
    updateProjectData({ constraints })
    setStep(6)
  }

  const handleBack = () => {
    updateProjectData({ constraints })
    setStep(4)
  }

  return (
    <OnboardingCard>
      <OnboardingCardHeader>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
          <Lock className="h-7 w-7 text-primary" />
        </div>
        <OnboardingCardTitle>Design constraints</OnboardingCardTitle>
        <OnboardingCardDescription>
          Set any restrictions for the optimization
        </OnboardingCardDescription>
      </OnboardingCardHeader>
      <OnboardingCardContent>
        <div className="space-y-4">
          {constraintOptions.map((option) => {
            const Icon = option.icon
            return (
              <div
                key={option.key}
                className="flex items-center justify-between rounded-xl border p-4 transition-colors hover:bg-muted/50"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                    <Icon className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <div className="font-medium">{option.label}</div>
                    <div className="text-sm text-muted-foreground">
                      {option.description}
                    </div>
                  </div>
                </div>
                <Switch
                  checked={constraints[option.key]}
                  onCheckedChange={() => handleToggle(option.key)}
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
