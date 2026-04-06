"use client"

import { useOnboarding } from "@/lib/onboarding-context"
import { OnboardingFlow } from "./onboarding/onboarding-flow"
import { Workspace } from "./workspace/workspace"

export function App() {
  const { isOnboardingComplete, selectedProjectId } = useOnboarding()

  if (isOnboardingComplete) {
    return <Workspace initialProjectId={selectedProjectId} />
  }

  return <OnboardingFlow />
}
