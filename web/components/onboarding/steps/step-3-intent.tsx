"use client"

import { useState } from "react"
import { useOnboarding } from "@/lib/onboarding-context"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  OnboardingCard,
  OnboardingCardHeader,
  OnboardingCardTitle,
  OnboardingCardDescription,
  OnboardingCardContent,
  OnboardingCardFooter,
} from "../onboarding-card"
import { ArrowRight, ArrowLeft, Layers } from "lucide-react"
import { cn } from "@/lib/utils"

const buildingTypes = [
  { value: "residential", label: "Residential" },
  { value: "office", label: "Office" },
  { value: "mixed-use", label: "Mixed-Use" },
  { value: "retail", label: "Retail" },
  { value: "hospitality", label: "Hospitality" },
]

const scales = [
  { value: "low-rise", label: "Low-rise", description: "1-4 floors" },
  { value: "mid-rise", label: "Mid-rise", description: "5-12 floors" },
  { value: "high-rise", label: "High-rise", description: "13+ floors" },
]

export function Step3Intent() {
  const { projectData, updateProjectData, setStep } = useOnboarding()
  const [buildingType, setBuildingType] = useState(projectData.buildingType)
  const [scale, setScale] = useState(projectData.scale)

  const handleContinue = () => {
    updateProjectData({ buildingType, scale })
    setStep(4)
  }

  const handleBack = () => {
    updateProjectData({ buildingType, scale })
    setStep(2)
  }

  return (
    <OnboardingCard>
      <OnboardingCardHeader>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
          <Layers className="h-7 w-7 text-primary" />
        </div>
        <OnboardingCardTitle>What are you building?</OnboardingCardTitle>
        <OnboardingCardDescription>
          Tell us about your building type and scale
        </OnboardingCardDescription>
      </OnboardingCardHeader>
      <OnboardingCardContent>
        <div className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Building Type</label>
            <Select value={buildingType} onValueChange={setBuildingType}>
              <SelectTrigger className="h-12 w-full">
                <SelectValue placeholder="Select building type" />
              </SelectTrigger>
              <SelectContent>
                {buildingTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-3">
            <label className="text-sm font-medium">Scale</label>
            <div className="grid grid-cols-3 gap-3">
              {scales.map((s) => (
                <button
                  key={s.value}
                  onClick={() => setScale(s.value)}
                  className={cn(
                    "rounded-xl border-2 p-4 text-center transition-all hover:border-primary/50",
                    scale === s.value
                      ? "border-primary bg-primary/5"
                      : "border-border"
                  )}
                >
                  <div className="font-medium">{s.label}</div>
                  <div className="text-xs text-muted-foreground">
                    {s.description}
                  </div>
                </button>
              ))}
            </div>
          </div>
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
            disabled={!buildingType || !scale}
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
