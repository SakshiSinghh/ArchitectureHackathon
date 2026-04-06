"use client"

import { createContext, useContext, useState, type ReactNode } from "react"

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
  completeOnboarding: () => void
  resetOnboarding: () => void
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

  const updateProjectData = (data: Partial<ProjectData>) => {
    setProjectData((prev) => ({ ...prev, ...data }))
  }

  const completeOnboarding = () => {
    setIsOnboardingComplete(true)
  }

  const resetOnboarding = () => {
    setStep(1)
    setProjectData(defaultProjectData)
    setIsOnboardingComplete(false)
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
