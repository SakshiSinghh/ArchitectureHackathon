"use client"

import { useState } from "react"
import { useOnboarding } from "@/lib/onboarding-context"
import { Button } from "@/components/ui/button"
import {
  OnboardingCard,
  OnboardingCardHeader,
  OnboardingCardTitle,
  OnboardingCardDescription,
  OnboardingCardContent,
  OnboardingCardFooter,
} from "../onboarding-card"
import { ArrowRight, ArrowLeft, Compass } from "lucide-react"
import { cn } from "@/lib/utils"

const orientations = [
  { value: "N", label: "North", angle: 0 },
  { value: "NE", label: "Northeast", angle: 45 },
  { value: "E", label: "East", angle: 90 },
  { value: "SE", label: "Southeast", angle: 135 },
  { value: "S", label: "South", angle: 180 },
  { value: "SW", label: "Southwest", angle: 225 },
  { value: "W", label: "West", angle: 270 },
  { value: "NW", label: "Northwest", angle: 315 },
]

export function Step4Orientation() {
  const { projectData, updateProjectData, setStep } = useOnboarding()
  const [orientation, setOrientation] = useState(projectData.orientation)

  const handleContinue = () => {
    updateProjectData({ orientation })
    setStep(5)
  }

  const handleBack = () => {
    updateProjectData({ orientation })
    setStep(3)
  }

  const selectedOrientation = orientations.find((o) => o.value === orientation)

  return (
    <OnboardingCard>
      <OnboardingCardHeader>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
          <Compass className="h-7 w-7 text-primary" />
        </div>
        <OnboardingCardTitle>Building orientation</OnboardingCardTitle>
        <OnboardingCardDescription>
          Select the primary facing direction of your building
        </OnboardingCardDescription>
      </OnboardingCardHeader>
      <OnboardingCardContent>
        <div className="flex flex-col items-center gap-6">
          <div className="relative h-56 w-56">
            {/* Compass Background */}
            <div className="absolute inset-0 rounded-full border-2 border-muted" />
            <div className="absolute inset-4 rounded-full border border-muted/50" />
            
            {/* Compass Needle - rotates around center */}
            <div
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 transition-transform duration-300"
              style={{
                transform: `translate(-50%, -50%) rotate(${selectedOrientation?.angle || 0}deg)`,
              }}
            >
              {/* Red needle pointing to selected direction */}
              <svg width="20" height="80" viewBox="0 0 20 80" className="absolute left-1/2 -translate-x-1/2 -translate-y-full">
                <polygon points="10,0 4,35 10,30 16,35" fill="#dc2626" />
                <polygon points="10,30 4,35 10,40 16,35" fill="#991b1b" />
              </svg>
              {/* White/gray needle pointing opposite */}
              <svg width="20" height="80" viewBox="0 0 20 80" className="absolute left-1/2 top-0 -translate-x-1/2 rotate-180">
                <polygon points="10,0 4,35 10,30 16,35" fill="#e5e7eb" />
                <polygon points="10,30 4,35 10,40 16,35" fill="#d1d5db" />
              </svg>
            </div>
            
            {/* Center Point */}
            <div className="absolute left-1/2 top-1/2 h-5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-foreground shadow-md z-10" />
            
            {/* Direction Buttons */}
            {orientations.map((o) => {
              const angle = (o.angle - 90) * (Math.PI / 180)
              const radius = 100
              const x = Math.cos(angle) * radius
              const y = Math.sin(angle) * radius
              
              return (
                <button
                  key={o.value}
                  onClick={() => setOrientation(o.value)}
                  className={cn(
                    "absolute flex h-10 w-10 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full text-xs font-semibold transition-all",
                    orientation === o.value
                      ? "bg-primary text-primary-foreground shadow-lg"
                      : "bg-muted hover:bg-muted/80"
                  )}
                  style={{
                    left: `calc(50% + ${x}px)`,
                    top: `calc(50% + ${y}px)`,
                  }}
                >
                  {o.value}
                </button>
              )
            })}
          </div>
          <p className="text-sm text-muted-foreground">
            Selected: <span className="font-medium text-foreground">{selectedOrientation?.label}</span>
          </p>
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
