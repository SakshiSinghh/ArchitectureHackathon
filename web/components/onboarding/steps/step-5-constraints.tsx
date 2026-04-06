"use client"

import { useState } from "react"
import { interpretConstraints } from "@/lib/api-client"
import { useOnboarding } from "@/lib/onboarding-context"
import { onboardingToProjectState } from "@/lib/project-mappers"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import {
  OnboardingCard,
  OnboardingCardHeader,
  OnboardingCardTitle,
  OnboardingCardDescription,
  OnboardingCardContent,
  OnboardingCardFooter,
} from "../onboarding-card"
import { ArrowRight, ArrowLeft, Lock, RotateCcw, Layers, ArrowUpFromLine } from "lucide-react"

const constraintOptions = [
  {
    key: "lockOrientation" as const,
    label: "Lock Orientation",
    description: "Keep the building facing fixed",
    icon: RotateCcw,
  },
  {
    key: "lockFacade" as const,
    label: "Lock Facade",
    description: "Preserve the exterior design",
    icon: Layers,
  },
  {
    key: "heightRestriction" as const,
    label: "Height Restriction",
    description: "Apply local zoning limits",
    icon: ArrowUpFromLine,
  },
]

export function Step5Constraints() {
  const { projectData, updateProjectData, setStep } = useOnboarding()
  const [constraints, setConstraints] = useState(projectData.constraints)
  const [freeTextConstraints, setFreeTextConstraints] = useState(projectData.freeTextConstraints)
  const [parsedConstraints, setParsedConstraints] = useState(projectData.parsedConstraints)
  const [isInterpreting, setIsInterpreting] = useState(false)
  const [interpretError, setInterpretError] = useState<string | null>(null)

  const handleToggle = (key: keyof typeof constraints) => {
    setConstraints((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const handleContinue = () => {
    updateProjectData({ constraints, freeTextConstraints, parsedConstraints })
    setStep(6)
  }

  const handleBack = () => {
    updateProjectData({ constraints, freeTextConstraints, parsedConstraints })
    setStep(4)
  }

  const handleInterpret = async () => {
    setInterpretError(null)
    setIsInterpreting(true)
    try {
      const draft = {
        ...projectData,
        constraints,
        freeTextConstraints,
        parsedConstraints,
      }
      const response = await interpretConstraints(onboardingToProjectState(draft))
      setParsedConstraints(response.parsed_constraints)
    } catch (error) {
      setInterpretError(error instanceof Error ? error.message : "Failed to interpret constraints")
    } finally {
      setIsInterpreting(false)
    }
  }

  const setParsedItemStatus = (index: number, status: "proposed" | "accepted" | "rejected" | "edited") => {
    setParsedConstraints((prev) => ({
      ...prev,
      extracted_items: prev.extracted_items.map((item, itemIndex) =>
        itemIndex === index ? { ...item, status } : item
      ),
    }))
  }

  const setParsedItemValue = (index: number, rawValue: string) => {
    const normalizedValue: string | number | boolean | null =
      rawValue.toLowerCase() === "true"
        ? true
        : rawValue.toLowerCase() === "false"
          ? false
          : rawValue === ""
            ? null
            : Number.isNaN(Number(rawValue))
              ? rawValue
              : Number(rawValue)
    setParsedConstraints((prev) => ({
      ...prev,
      extracted_items: prev.extracted_items.map((item, itemIndex) =>
        itemIndex === index
          ? {
              ...item,
              normalized_value: normalizedValue,
              status: item.status === "rejected" ? "edited" : "edited",
            }
          : item
      ),
    }))
  }

  return (
    <OnboardingCard>
      <OnboardingCardHeader>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
          <Lock className="h-7 w-7 text-primary" />
        </div>
        <OnboardingCardTitle>Design constraints</OnboardingCardTitle>
        <OnboardingCardDescription>
          Set any restrictions for the optimization
        </OnboardingCardDescription>
      </OnboardingCardHeader>
      <OnboardingCardContent>
        <div className="space-y-4">
          {constraintOptions.map((option) => {
            const Icon = option.icon
            return (
              <div
                key={option.key}
                className="flex items-center justify-between rounded-xl border p-4 transition-colors hover:bg-muted/50"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                    <Icon className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <div className="font-medium">{option.label}</div>
                    <div className="text-sm text-muted-foreground">
                      {option.description}
                    </div>
                  </div>
                </div>
                <Switch
                  checked={constraints[option.key]}
                  onCheckedChange={() => handleToggle(option.key)}
                />
              </div>
            )
          })}

          <div className="rounded-xl border p-4">
            <div className="mb-2 text-sm font-medium">Written constraints (optional)</div>
            <p className="mb-3 text-xs text-muted-foreground">
              Add natural-language constraints and click Interpret to generate proposed structured constraints.
              Review each item and mark it accepted, edited, or rejected.
            </p>
            <Textarea
              placeholder="Example: Orientation cannot change due to site access. Height capped at 8 floors."
              value={freeTextConstraints}
              onChange={(event) => setFreeTextConstraints(event.target.value)}
              className="min-h-[110px]"
            />
            <div className="mt-3 flex items-center gap-3">
              <Button type="button" variant="outline" onClick={handleInterpret} disabled={isInterpreting || !freeTextConstraints.trim()}>
                {isInterpreting ? "Interpreting..." : "Interpret"}
              </Button>
              <span className="text-xs text-muted-foreground">
                Mode: {parsedConstraints.parser_mode} · Confidence: {Math.round((parsedConstraints.confidence_score || 0) * 100)}%
              </span>
            </div>
            {interpretError ? <p className="mt-2 text-xs text-destructive">{interpretError}</p> : null}

            {parsedConstraints.extracted_items.length > 0 ? (
              <div className="mt-4 space-y-3 rounded-lg border p-3">
                <div className="text-xs font-semibold text-muted-foreground">Interpreted constraints</div>
                {parsedConstraints.extracted_items.map((item, index) => (
                  <div key={`${item.normalized_key}-${index}`} className="rounded-md border p-2">
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <div className="text-sm font-medium">{item.normalized_key}</div>
                      <Badge variant="secondary" className="text-[10px]">
                        {Math.round(item.confidence * 100)}%
                      </Badge>
                    </div>
                    <div className="mb-2 text-xs text-muted-foreground">Source: {item.source_text}</div>
                    <div className="grid gap-2 sm:grid-cols-2">
                      <input
                        className="h-9 rounded-md border px-2 text-sm"
                        value={item.normalized_value == null ? "" : String(item.normalized_value)}
                        onChange={(event) => setParsedItemValue(index, event.target.value)}
                        placeholder="Normalized value"
                      />
                      <select
                        className="h-9 rounded-md border bg-background px-2 text-sm"
                        value={item.status}
                        onChange={(event) =>
                          setParsedItemStatus(index, event.target.value as "proposed" | "accepted" | "rejected" | "edited")
                        }
                      >
                        <option value="proposed">Proposed</option>
                        <option value="accepted">Accepted</option>
                        <option value="edited">Edited</option>
                        <option value="rejected">Rejected</option>
                      </select>
                    </div>
                    {item.rationale ? <p className="mt-1 text-xs text-muted-foreground">{item.rationale}</p> : null}
                  </div>
                ))}
              </div>
            ) : null}

            {parsedConstraints.unresolved_items.length > 0 ? (
              <div className="mt-3 rounded-md border border-amber-300/60 bg-amber-50 p-2 text-xs text-amber-900">
                <div className="font-medium">Unresolved phrases</div>
                <ul className="mt-1 list-disc pl-4">
                  {parsedConstraints.unresolved_items.map((value, index) => (
                    <li key={`${value}-${index}`}>{value}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
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
