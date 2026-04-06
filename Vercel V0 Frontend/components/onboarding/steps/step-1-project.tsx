"use client"

import { useState } from "react"
import { useOnboarding } from "@/lib/onboarding-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  OnboardingCard,
  OnboardingCardHeader,
  OnboardingCardTitle,
  OnboardingCardDescription,
  OnboardingCardContent,
  OnboardingCardFooter,
} from "../onboarding-card"
import { ArrowRight, Building2 } from "lucide-react"

export function Step1Project() {
  const { projectData, updateProjectData, setStep } = useOnboarding()
  const [name, setName] = useState(projectData.name)

  const handleContinue = () => {
    updateProjectData({ name })
    setStep(2)
  }

  return (
    <OnboardingCard>
      <OnboardingCardHeader>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
          <Building2 className="h-7 w-7 text-primary" />
        </div>
        <OnboardingCardTitle>{"Let's name your project"}</OnboardingCardTitle>
        <OnboardingCardDescription>
          Give your architectural project a memorable name
        </OnboardingCardDescription>
      </OnboardingCardHeader>
      <OnboardingCardContent>
        <div className="space-y-2">
          <Input
            type="text"
            placeholder="Urban Residence Tower"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="h-12 text-base"
            autoFocus
          />
        </div>
      </OnboardingCardContent>
      <OnboardingCardFooter>
        <Button
          onClick={handleContinue}
          disabled={!name.trim()}
          size="lg"
          className="gap-2"
        >
          Start project
          <ArrowRight className="h-4 w-4" />
        </Button>
      </OnboardingCardFooter>
    </OnboardingCard>
  )
}
