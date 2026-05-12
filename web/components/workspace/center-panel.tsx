"use client"

import { useEffect, useMemo, useState } from "react"
import { interpretConstraints } from "@/lib/api-client"
import { FloorPlanUpload } from "@/components/workspace/floor-plan-upload"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Save, Play, Layers, Lock, SlidersHorizontal, Compass, Building2, MapPin } from "lucide-react"
import type { FloorPlanAnalysis, ProjectState } from "@/lib/api-types"

type CenterPanelProps = {
  projectId: string | null
  state: ProjectState | null
  onStateChange: (next: ProjectState | null) => void
  onSave: () => Promise<void>
  onRun: () => Promise<void>
  isSaving: boolean
  isRunning: boolean
  error: string | null
}

const buildingTypes = [
  { value: "residential", label: "Residential" },
  { value: "office", label: "Office" },
  { value: "mixed-use", label: "Mixed-Use" },
  { value: "retail", label: "Retail" },
  { value: "hospitality", label: "Hospitality" },
]

const orientationChoices = [0, 45, 90, 135, 180, 225, 270, 315]

function parseConstraintLines(raw: string): string[] {
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
}

function formatConstraintLines(values: string[] | undefined): string {
  return (values || []).join("\n")
}

export function CenterPanel({
  projectId,
  state,
  onStateChange,
  onSave,
  onRun,
  isSaving,
  isRunning,
  error,
}: CenterPanelProps) {
  const [localData, setLocalData] = useState<ProjectState | null>(state)
  const [hasChanges, setHasChanges] = useState(false)
  const [isInterpreting, setIsInterpreting] = useState(false)
  const [interpretError, setInterpretError] = useState<string | null>(null)

  useEffect(() => {
    setLocalData(state)
    setHasChanges(false)
  }, [state])

  const hardConstraintsText = useMemo(
    () => formatConstraintLines(localData?.constraints.hard_constraints),
    [localData?.constraints.hard_constraints]
  )
  const softConstraintsText = useMemo(
    () => formatConstraintLines(localData?.constraints.soft_constraints),
    [localData?.constraints.soft_constraints]
  )

  const handleChange = <K extends keyof ProjectState>(
    key: K,
    value: ProjectState[K]
  ) => {
    setLocalData((prev) => (prev ? { ...prev, [key]: value } : prev))
    setHasChanges(true)
  }

  const handleConstraintChange = (key: "hard_constraints" | "soft_constraints", value: string) => {
    setLocalData((prev) => ({
      ...(prev as ProjectState),
      constraints: {
        ...((prev as ProjectState).constraints || {
          hard_constraints: [],
          soft_constraints: [],
          free_text: "",
          structured_enabled: true,
          notes: null,
        }),
        [key]: parseConstraintLines(value),
      },
    }))
    setHasChanges(true)
  }

  const handlePriorityChange = (key: keyof ProjectState["priorities"], value: number[]) => {
    setLocalData((prev) => ({
      ...(prev as ProjectState),
      priorities: { ...(prev as ProjectState).priorities, [key]: value[0] },
    }))
    setHasChanges(true)
  }

  const handleInterpretConstraints = async () => {
    if (!localData) {
      return
    }

    setInterpretError(null)
    setIsInterpreting(true)
    try {
      const response = await interpretConstraints(localData)
      setLocalData((prev) => (prev ? { ...prev, parsed_constraints: response.parsed_constraints } : prev))
      setHasChanges(true)
    } catch (error) {
      setInterpretError(error instanceof Error ? error.message : "Failed to interpret constraints")
    } finally {
      setIsInterpreting(false)
    }
  }

  const setParsedItemStatus = (index: number, status: "proposed" | "accepted" | "rejected" | "edited") => {
    setLocalData((prev) => {
      if (!prev) {
        return prev
      }
      return {
        ...prev,
        parsed_constraints: {
          ...prev.parsed_constraints,
          extracted_items: prev.parsed_constraints.extracted_items.map((item, itemIndex) =>
            itemIndex === index ? { ...item, status } : item
          ),
        },
      }
    })
    setHasChanges(true)
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

    setLocalData((prev) => {
      if (!prev) {
        return prev
      }
      return {
        ...prev,
        parsed_constraints: {
          ...prev.parsed_constraints,
          extracted_items: prev.parsed_constraints.extracted_items.map((item, itemIndex) =>
            itemIndex === index ? { ...item, normalized_value: normalizedValue, status: "edited" } : item
          ),
        },
      }
    })
    setHasChanges(true)
  }

  const commitSave = async () => {
    if (!localData) {
      return
    }
    onStateChange(localData)
    await onSave()
    setHasChanges(false)
  }

  const commitRun = async () => {
    if (!localData) {
      return
    }
    onStateChange(localData)
    await onRun()
    setHasChanges(false)
  }

  if (!localData) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        Select or create a project to begin.
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b px-6">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-semibold">{localData.project_name}</h1>
          {projectId ? <Badge variant="outline">{projectId}</Badge> : null}
          {hasChanges && (
            <Badge variant="secondary" className="text-xs">
              Unsaved changes
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={commitSave} disabled={isSaving || (!hasChanges && !projectId)}>
            <Save className="mr-2 h-4 w-4" />
            {isSaving ? "Saving..." : "Save"}
          </Button>
          <Button onClick={commitRun} disabled={isRunning}>
            <Play className="mr-2 h-4 w-4" />
            {isRunning ? "Running..." : "Run Analysis"}
          </Button>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 min-h-0">
        <div className="grid gap-6 p-6">
          {/* Review Mode */}
          {projectId && (
            <FloorPlanUpload
              projectId={projectId}
              onAnalysisComplete={(_analysis: FloorPlanAnalysis) => {
                // Analysis is persisted server-side; reload state to reflect inferred fields
                onStateChange(null)
                setTimeout(() => onStateChange(localData), 0)
              }}
            />
          )}
          {/* Project Info */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-base">
                <Building2 className="h-4 w-4" />
                Project Information
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Project Name</label>
                <Input
                  value={localData.project_name}
                  onChange={(e) => handleChange("project_name", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <MapPin className="h-3.5 w-3.5" />
                  Location
                </label>
                <Input
                  value={localData.site.location_name || ""}
                  onChange={(e) =>
                    setLocalData((prev) =>
                      prev
                        ? {
                            ...prev,
                            site: { ...prev.site, location_name: e.target.value || null },
                          }
                        : prev
                    )
                  }
                />
              </div>
            </CardContent>
          </Card>

          {/* Design Intent */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-base">
                <Layers className="h-4 w-4" />
                Design Intent
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-2">
                <label className="text-sm font-medium">Building Type</label>
                <Select
                  value={localData.building.building_type || "office"}
                  onValueChange={(value) =>
                    setLocalData((prev) =>
                      prev
                        ? {
                            ...prev,
                            building: { ...prev.building, building_type: value },
                          }
                        : prev
                    )
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
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
              <div className="space-y-2">
                <label className="text-sm font-medium">Floors</label>
                <Input
                  type="number"
                  min={1}
                  value={localData.building.floors ?? 1}
                  onChange={(event) =>
                    setLocalData((prev) =>
                      prev
                        ? {
                            ...prev,
                            building: { ...prev.building, floors: Number(event.target.value) },
                          }
                        : prev
                    )
                  }
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Compass className="h-3.5 w-3.5" />
                  Orientation (deg)
                </label>
                <Select
                  value={String(localData.building.orientation_deg ?? 0)}
                  onValueChange={(value) =>
                    setLocalData((prev) =>
                      prev
                        ? {
                            ...prev,
                            building: { ...prev.building, orientation_deg: Number(value) },
                          }
                        : prev
                    )
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {orientationChoices.map((o) => (
                      <SelectItem key={o} value={o}>
                        {o}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Constraints */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-base">
                <Lock className="h-4 w-4" />
                Constraints
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Structured constraints enabled</label>
                  <div className="flex items-center justify-between rounded-lg border p-3">
                    <span className="text-sm text-muted-foreground">Use structured hard and soft constraint lists</span>
                    <Switch
                      checked={Boolean(localData.constraints.structured_enabled)}
                      onCheckedChange={(checked) =>
                        setLocalData((prev) =>
                          prev
                            ? {
                                ...prev,
                                constraints: { ...prev.constraints, structured_enabled: checked },
                              }
                            : prev
                        )
                      }
                    />
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Hard constraints (structured)</label>
                    <Textarea
                      value={hardConstraintsText}
                      onChange={(event) => handleConstraintChange("hard_constraints", event.target.value)}
                      placeholder="One per line"
                      className="min-h-[100px]"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Soft constraints (structured)</label>
                    <Textarea
                      value={softConstraintsText}
                      onChange={(event) => handleConstraintChange("soft_constraints", event.target.value)}
                      placeholder="One per line"
                      className="min-h-[100px]"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Written constraints (free text)</label>
                  <Textarea
                    value={localData.constraints.free_text || ""}
                    onChange={(event) =>
                      setLocalData((prev) =>
                        prev
                          ? {
                              ...prev,
                              constraints: {
                                ...prev.constraints,
                                free_text: event.target.value,
                                notes: event.target.value ? "Free-text constraints available for interpretation." : null,
                              },
                            }
                          : prev
                      )
                    }
                    placeholder="Orientation cannot change due to site access. Height capped at 8 floors."
                    className="min-h-[110px]"
                  />
                  <div className="flex items-center gap-3">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleInterpretConstraints}
                      disabled={isInterpreting || !String(localData.constraints.free_text || "").trim()}
                    >
                      {isInterpreting ? "Interpreting..." : "Interpret"}
                    </Button>
                    <span className="text-xs text-muted-foreground">
                      Mode: {localData.parsed_constraints.parser_mode} · Confidence: {Math.round(localData.parsed_constraints.confidence_score * 100)}%
                    </span>
                  </div>
                  {interpretError ? <p className="text-xs text-destructive">{interpretError}</p> : null}

                  {localData.parsed_constraints.extracted_items.length > 0 ? (
                    <div className="space-y-3 rounded-lg border p-3">
                      <div className="text-xs font-semibold text-muted-foreground">Interpreted constraints</div>
                      {localData.parsed_constraints.extracted_items.map((item, index) => (
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

                  {localData.parsed_constraints.unresolved_items.length > 0 ? (
                    <div className="rounded-md border border-amber-300/60 bg-amber-50 p-2 text-xs text-amber-900">
                      <div className="font-medium">Unresolved phrases</div>
                      <ul className="mt-1 list-disc pl-4">
                        {localData.parsed_constraints.unresolved_items.map((value, index) => (
                          <li key={`${value}-${index}`}>{value}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}

                  {localData.parsed_constraints.conflict_warnings.length > 0 ? (
                    <div className="rounded-md border border-amber-300/60 bg-amber-50 p-2 text-xs text-amber-900">
                      <div className="font-medium">Conflict warnings</div>
                      <ul className="mt-1 list-disc pl-4">
                        {localData.parsed_constraints.conflict_warnings.map((value, index) => (
                          <li key={`${value}-${index}`}>{value}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Priorities */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-base">
                <SlidersHorizontal className="h-4 w-4" />
                Priorities
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 sm:grid-cols-2">
                {(
                  [
                    { key: "daylight", label: "Daylight" },
                    { key: "energy", label: "Energy Efficiency" },
                    { key: "ventilation", label: "Ventilation" },
                    { key: "cost", label: "Cost" },
                    { key: "aesthetics", label: "Aesthetics" },
                  ] as const
                ).map((priority) => (
                  <div key={priority.key} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{priority.label}</span>
                      <span className="text-sm font-semibold tabular-nums text-muted-foreground">
                        {(localData.priorities[priority.key] * 100).toFixed(0)}%
                      </span>
                    </div>
                    <Slider
                      value={[Math.round(localData.priorities[priority.key] * 100)]}
                      onValueChange={(value) =>
                        handlePriorityChange(priority.key, [Number((value[0] / 100).toFixed(3))])
                      }
                      max={100}
                      step={5}
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {error ? (
            <Card className="border-destructive/40">
              <CardContent className="pt-6 text-sm text-destructive">{error}</CardContent>
            </Card>
          ) : null}
        </div>
      </ScrollArea>
    </div>
  )
}
