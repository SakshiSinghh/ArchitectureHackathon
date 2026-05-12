"use client"

import { useOnboarding } from "@/lib/onboarding-context"
import { StepIndicator } from "./step-indicator"
import { Step1Project } from "./steps/step-1-project"
import { Step2Location } from "./steps/step-2-location"
import { Step3Intent } from "./steps/step-3-intent"
import { Step4Orientation } from "./steps/step-4-orientation"
import { Step5Constraints } from "./steps/step-5-constraints"
import { Step6Priorities } from "./steps/step-6-priorities"
import { Step7Summary } from "./steps/step-7-summary"

export function OnboardingFlow() {
  const { step } = useOnboarding()

  const renderStep = () => {
    switch (step) {
      case 1:
        return <Step1Project />
      case 2:
        return <Step2Location />
      case 3:
        return <Step3Intent />
      case 4:
        return <Step4Orientation />
      case 5:
        return <Step5Constraints />
      case 6:
        return <Step6Priorities />
      case 7:
        return <Step7Summary />
      default:
        return <Step1Project />
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="fixed inset-x-0 top-0 z-50 border-b bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex h-16 max-w-screen-xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <span className="text-sm font-bold text-primary-foreground">A</span>
            </div>
            <span className="text-lg font-semibold">ArchEnv</span>
          </div>
          <StepIndicator />
          <div className="w-24" /> {/* Spacer for centering */}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex flex-1 items-center justify-center px-6 pt-24 pb-12">
        {renderStep()}
      </main>
    </div>
  )
}
