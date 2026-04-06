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
import { ArrowRight, ArrowLeft, MapPin } from "lucide-react"

export function Step2Location() {
  const { projectData, updateProjectData, setStep } = useOnboarding()
  const [location, setLocation] = useState(projectData.location)

  const handleContinue = () => {
    updateProjectData({ location })
    setStep(3)
  }

  const handleBack = () => {
    updateProjectData({ location })
    setStep(1)
  }

  return (
    <OnboardingCard>
      <OnboardingCardHeader>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
          <MapPin className="h-7 w-7 text-primary" />
        </div>
        <OnboardingCardTitle>Where is your project located?</OnboardingCardTitle>
        <OnboardingCardDescription>
          {"We'll use this for climate and environmental analysis"}
        </OnboardingCardDescription>
      </OnboardingCardHeader>
      <OnboardingCardContent>
        <div className="space-y-2">
          <Input
            type="text"
            placeholder="New York, NY or 40.7128, -74.0060"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="h-12 text-base"
            autoFocus
          />
          <p className="text-xs text-muted-foreground">
            Enter a city name or coordinates
          </p>
        </div>
      </OnboardingCardContent>
      <OnboardingCardFooter>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleBack} size="lg">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Button
            onClick={handleContinue}
            disabled={!location.trim()}
            size="lg"
            className="gap-2"
          >
            Continue
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </OnboardingCardFooter>
    </OnboardingCard>
  )
}
