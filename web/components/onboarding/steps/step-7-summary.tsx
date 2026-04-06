"use client"

import { useState } from "react"
import { useOnboarding } from "@/lib/onboarding-context"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { createProject, updateProject } from "@/lib/api-client"
import { onboardingToProjectState } from "@/lib/project-mappers"
import {
  OnboardingCard,
  OnboardingCardHeader,
  OnboardingCardTitle,
  OnboardingCardDescription,
  OnboardingCardContent,
  OnboardingCardFooter,
} from "../onboarding-card"
import { ArrowLeft, Sparkles, Building2, MapPin, Layers, Compass, Lock, SlidersHorizontal } from "lucide-react"

export function Step7Summary() {
  const { projectData, setStep, completeOnboarding } = useOnboarding()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleBack = () => {
    setStep(6)
  }

  const handleGenerate = async () => {
    setError(null)
    setIsSubmitting(true)
    try {
      const created = await createProject({
        project_name: projectData.name,
        brief_text: `Onboarding seed for ${projectData.name}`,
      })

      const initialState = onboardingToProjectState(projectData)
      await updateProject(created.project.project_id, initialState)
      completeOnboarding(created.project.project_id)
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Could not create project"
      setError(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const formatScale = (scale: string) => {
    return scale
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join("-")
  }

  const formatBuildingType = (type: string) => {
    return type
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  }

  const activeConstraints = Object.entries(projectData.constraints)
    .filter(([, value]) => value)
    .map(([key]) => key)

  return (
    <OnboardingCard className="max-w-xl">
      <OnboardingCardHeader>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
          <Sparkles className="h-7 w-7 text-primary" />
        </div>
        <OnboardingCardTitle>Ready to analyze</OnboardingCardTitle>
        <OnboardingCardDescription>
          Review your project settings before generating the baseline
        </OnboardingCardDescription>
      </OnboardingCardHeader>
      <OnboardingCardContent>
        <div className="space-y-4">
          <div className="rounded-xl border bg-muted/30 p-4">
            <div className="grid gap-4">
              <div className="flex items-start gap-3">
                <Building2 className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="text-xs text-muted-foreground">Project Name</div>
                  <div className="font-medium">{projectData.name}</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <MapPin className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="text-xs text-muted-foreground">Location</div>
                  <div className="font-medium">{projectData.location}</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <Layers className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="text-xs text-muted-foreground">Building Type & Scale</div>
                  <div className="font-medium">
                    {formatBuildingType(projectData.buildingType)} · {formatScale(projectData.scale)}
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <Compass className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="text-xs text-muted-foreground">Orientation</div>
                  <div className="font-medium">{projectData.orientation}</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <Lock className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="text-xs text-muted-foreground">Constraints</div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {activeConstraints.length > 0 ? (
                      activeConstraints.map((constraint) => (
                        <Badge key={constraint} variant="secondary" className="text-xs">
                          {constraint === "lockOrientation" && "Orientation Locked"}
                          {constraint === "lockFacade" && "Facade Locked"}
                          {constraint === "heightRestriction" && "Height Limited"}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-muted-foreground">No constraints</span>
                    )}
                  </div>
                  {projectData.freeTextConstraints ? (
                    <p className="mt-2 text-xs text-muted-foreground">Written: {projectData.freeTextConstraints}</p>
                  ) : null}
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <SlidersHorizontal className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="text-xs text-muted-foreground">Priorities</div>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    <div className="flex justify-between text-sm">
                      <span>Daylight</span>
                      <span className="font-medium">{projectData.priorities.daylight}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Energy</span>
                      <span className="font-medium">{projectData.priorities.energyEfficiency}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Cost</span>
                      <span className="font-medium">{projectData.priorities.cost}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Aesthetics</span>
                      <span className="font-medium">{projectData.priorities.aesthetics}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        {error ? <p className="pt-3 text-sm text-destructive">{error}</p> : null}
      </OnboardingCardContent>
      <OnboardingCardFooter>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleBack} size="lg">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Button onClick={handleGenerate} size="lg" className="gap-2" disabled={isSubmitting}>
            <Sparkles className="h-4 w-4" />
            {isSubmitting ? "Creating project..." : "Generate baseline analysis"}
          </Button>
        </div>
      </OnboardingCardFooter>
    </OnboardingCard>
  )
}
