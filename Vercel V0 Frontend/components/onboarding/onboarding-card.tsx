"use client"

import { type ReactNode } from "react"
import { cn } from "@/lib/utils"

type OnboardingCardProps = {
  children: ReactNode
  className?: string
}

export function OnboardingCard({ children, className }: OnboardingCardProps) {
  return (
    <div
      className={cn(
        "w-full max-w-lg rounded-2xl bg-card p-8 shadow-xl shadow-black/5 transition-all duration-500 animate-in fade-in-0 slide-in-from-bottom-4",
        className
      )}
    >
      {children}
    </div>
  )
}

export function OnboardingCardHeader({ children }: { children: ReactNode }) {
  return <div className="mb-8 space-y-2 text-center">{children}</div>
}

export function OnboardingCardTitle({ children }: { children: ReactNode }) {
  return (
    <h2 className="text-2xl font-semibold tracking-tight text-balance">
      {children}
    </h2>
  )
}

export function OnboardingCardDescription({
  children,
}: {
  children: ReactNode
}) {
  return (
    <p className="text-muted-foreground text-balance">{children}</p>
  )
}

export function OnboardingCardContent({ children }: { children: ReactNode }) {
  return <div className="space-y-6">{children}</div>
}

export function OnboardingCardFooter({ children }: { children: ReactNode }) {
  return <div className="mt-8 flex justify-center">{children}</div>
}
