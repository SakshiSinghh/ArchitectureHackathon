"use client"

import { OnboardingProvider } from "@/lib/onboarding-context"
import { App } from "@/components/app"

export default function Home() {
  return (
    <OnboardingProvider>
      <App />
    </OnboardingProvider>
  )
}
