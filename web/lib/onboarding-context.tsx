"use client"

import { createContext, useContext, useState, type ReactNode } from "react"

import type { ParsedConstraints } from "@/lib/api-types"

export type ProjectData = {
  name: string
  location: string
  buildingType: string
  scale: string
  orientation: string
  constraints: {
    lockOrientation: boolean
    lockFacade: boolean
    heightRestriction: boolean
  }
  freeTextConstraints: string
  parsedConstraints: ParsedConstraints
  priorities: {
    daylight: number
    energyEfficiency: number
    cost: number
    aesthetics: number
  }
}

type OnboardingContextType = {
  step: number
  setStep: (step: number) => void
  projectData: ProjectData
  updateProjectData: (data: Partial<ProjectData>) => void
  isOnboardingComplete: boolean
  completeOnboarding: (projectId: string) => void
  resetOnboarding: () => void
  selectedProjectId: string | null
  setSelectedProjectId: (projectId: string | null) => void
}

const defaultProjectData: ProjectData = {
  name: "",
  location: "",
  buildingType: "",
  scale: "",
  orientation: "N",
  constraints: {
    lockOrientation: false,
    lockFacade: false,
    heightRestriction: false,
  },
  freeTextConstraints: "",
  parsedConstraints: {
    extracted_items: [],
    unresolved_items: [],
    confidence_label: "low",
    confidence_score: 0,
    parser_provider: "none",
    parser_mode: "none",
    notes: [],
    conflict_warnings: [],
  },
  priorities: {
    daylight: 50,
    energyEfficiency: 50,
    cost: 50,
    aesthetics: 50,
  },
}

const OnboardingContext = createContext<OnboardingContextType | null>(null)

export function OnboardingProvider({ children }: { children: ReactNode }) {
  const [step, setStep] = useState(1)
  const [projectData, setProjectData] = useState<ProjectData>(defaultProjectData)
  const [isOnboardingComplete, setIsOnboardingComplete] = useState(false)
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null)

  const updateProjectData = (data: Partial<ProjectData>) => {
    setProjectData((prev) => ({ ...prev, ...data }))
  }

  const completeOnboarding = (projectId: string) => {
    setSelectedProjectId(projectId)
    setIsOnboardingComplete(true)
  }

  const resetOnboarding = () => {
    setStep(1)
    setProjectData(defaultProjectData)
    setIsOnboardingComplete(false)
    setSelectedProjectId(null)
  }

  return (
    <OnboardingContext.Provider
      value={{
        step,
        setStep,
        projectData,
        updateProjectData,
        isOnboardingComplete,
        completeOnboarding,
        resetOnboarding,
        selectedProjectId,
        setSelectedProjectId,
      }}
    >
      {children}
    </OnboardingContext.Provider>
  )
}

export function useOnboarding() {
  const context = useContext(OnboardingContext)
  if (!context) {
    throw new Error("useOnboarding must be used within an OnboardingProvider")
  }
  return context
}
