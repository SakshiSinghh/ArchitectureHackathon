"use client"

import { useEffect, useMemo, useState } from "react"
import { interpretConstraints } from "@/lib/api-client"
import { FloorPlanUpload } from "@/components/workspace/floor-plan-upload"
import { OrientationOptions } from "@/components/workspace/orientation-options"
import { GrasshopperPanel } from "@/components/workspace/grasshopper-panel"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import {
  Save, Play, Layers, Lock, SlidersHorizontal, Compass,
  Building2, MapPin, Thermometer, Sun, Wind, Lightbulb, ArrowRight,
  FolderOpen, BarChart2, Plug,
} from "lucide-react"
import { cn } from "@/lib/utils"
import type {
  AgentReviewResponse, FloorPlanAnalysis, OrientationOptionsResponse,
  ProjectState, RunDiff, RunSnapshot,
} from "@/lib/api-types"

type CenterPanelProps = {
  projectId: string | null
  state: ProjectState | null
  onStateChange: (next: ProjectState | null) => void
  onSave: () => Promise<void>
  onRun: () => Promise<void>
  isSaving: boolean
  isRunning: boolean
  error: string | null
  review: AgentReviewResponse | null
  diff: RunDiff | null
  run: RunSnapshot | null
  orientationOptions: OrientationOptionsResponse | null
  activeTab?: string
  onTabChange?: (tab: string) => void
}

const buildingTypes = [
  { value: "residential", label: "Residential" },
  { value: "office", label: "Office" },
  { value: "mixed-use", label: "Mixed-Use" },
  { value: "retail", label: "Retail" },
  { value: "hospitality", label: "Hospitality" },
]

const orientationChoices = [0, 45, 90, 135, 180, 225, 270, 315]
const orientationLabels: Record<number, string> = {
  0: "0 deg - North", 45: "45 deg - NE", 90: "90 deg - East",
  135: "135 deg - SE", 180: "180 deg - South",
  225: "225 deg - SW", 270: "270 deg - West", 315: "315 deg - NW",
}

function parseConstraintLines(raw: string): string[] {
  return raw.split("\n").map((l) => l.trim()).filter(Boolean)
}
function formatConstraintLines(values: string[] | undefined): string {
  return (values || []).join("\n")
}
function numeric(value: unknown): number {
  const p = Number(value)
  return Number.isFinite(p) ? p : 0
}

// ── Tab trigger shared class ───────────────────────────────────────────────
const triggerCls =
  "relative h-7 rounded-md px-4 text-xs font-medium gap-1.5 " +
  "transition-all duration-150 " +
  "text-muted-foreground hover:text-foreground " +
  "data-[state=active]:bg-background data-[state=active]:text-foreground " +
  "data-[state=active]:shadow-sm data-[state=active]:font-semibold"

export function CenterPanel({
  projectId, state, onStateChange, onSave, onRun,
  isSaving, isRunning, error,
  review, diff, run, orientationOptions,
  activeTab = "project", onTabChange,
}: CenterPanelProps) {
  const [localData, setLocalData] = useState<ProjectState | null>(state)
  const [hasChanges, setHasChanges] = useState(false)
  const [isInterpreting, setIsInterpreting] = useState(false)
  const [interpretError, setInterpretError] = useState<string | null>(null)

  useEffect(() => { setLocalData(state); setHasChanges(false) }, [state])

  const hardConstraintsText = useMemo(
    () => formatConstraintLines(localData?.constraints.hard_constraints),
    [localData?.constraints.hard_constraints]
  )
  const softConstraintsText = useMemo(
    () => formatConstraintLines(localData?.constraints.soft_constraints),
    [localData?.constraints.soft_constraints]
  )

  const handleConstraintChange = (key: "hard_constraints" | "soft_constraints", value: string) => {
    setLocalData((prev) => ({
      ...(prev as ProjectState),
      constraints: {
        ...((prev as ProjectState).constraints || { hard_constraints: [], soft_constraints: [], free_text: "", structured_enabled: true, notes: null }),
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
    if (!localData) return
    setInterpretError(null)
    setIsInterpreting(true)
    try {
      const response = await interpretConstraints(localData)
      setLocalData((prev) => (prev ? { ...prev, parsed_constraints: response.parsed_constraints } : prev))
      setHasChanges(true)
    } catch (err) {
      setInterpretError(err instanceof Error ? err.message : "Failed to interpret constraints")
    } finally {
      setIsInterpreting(false)
    }
  }

  const setParsedItemStatus = (index: number, status: "proposed" | "accepted" | "rejected" | "edited") => {
    setLocalData((prev) => {
      if (!prev) return prev
      return {
        ...prev,
        parsed_constraints: {
          ...prev.parsed_constraints,
          extracted_items: prev.parsed_constraints.extracted_items.map((item, i) =>
            i === index ? { ...item, status } : item
          ),
        },
      }
    })
    setHasChanges(true)
  }

  const setParsedItemValue = (index: number, rawValue: string) => {
    const normalizedValue =
      rawValue === "true" ? true
      : rawValue === "false" ? false
      : rawValue === "" ? null
      : Number.isNaN(Number(rawValue)) ? rawValue
      : Number(rawValue)
    setLocalData((prev) => {
      if (!prev) return prev
      return {
        ...prev,
        parsed_constraints: {
          ...prev.parsed_constraints,
          extracted_items: prev.parsed_constraints.extracted_items.map((item, i) =>
            i === index ? { ...item, normalized_value: normalizedValue, status: "edited" } : item
          ),
        },
      }
    })
    setHasChanges(true)
  }

  const commitSave = async () => {
    if (!localData) return
    onStateChange(localData)
    await onSave()
    setHasChanges(false)
  }

  const commitRun = async () => {
    if (!localData) return
    onStateChange(localData)
    await onRun()
    setHasChanges(false)
  }

  const b = state?.baseline_results
  const hasBaseline = b && (b.energy_risk != null || b.daylight_potential != null || b.ventilation_potential != null)
  const baselineMetrics = [
    { label: "Energy Risk", value: numeric(b?.energy_risk) * 100, icon: Thermometer, color: "[&>div]:bg-orange-500", hint: "Lower is better" },
    { label: "Daylight", value: numeric(b?.daylight_potential) * 100, icon: Sun, color: "[&>div]:bg-yellow-400", hint: "Higher is better" },
    { label: "Ventilation", value: numeric(b?.ventilation_potential) * 100, icon: Wind, color: "[&>div]:bg-sky-400", hint: "Higher is better" },
    { label: "Heat Exposure", value: numeric(b?.heat_exposure_score) * 100, icon: Thermometer, color: "[&>div]:bg-red-400", hint: "Lower is better" },
  ]
  const recommendations = review?.ranked_options || []

  if (!localData) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        Select or create a project to begin.
      </div>
    )
  }

  return (
    <Tabs value={activeTab} onValueChange={onTabChange} className="flex h-full flex-col min-h-0">

      {/* ── Unified navigation bar ────────────────────────────────────── */}
      <div className="flex h-14 shrink-0 items-center gap-4 border-b bg-background px-6">

        {/* Left — project name */}
        <div className="flex min-w-0 flex-1 items-center gap-2.5">
          <h1 className="truncate text-base font-semibold">{localData.project_name}</h1>
          {hasChanges && (
            <Badge variant="secondary" className="shrink-0 text-xs">Unsaved</Badge>
          )}
        </div>

        {/* Centre — segmented-control tabs */}
        <TabsList className="h-9 rounded-lg bg-muted/70 p-1 gap-0">
          <TabsTrigger value="project" className={triggerCls}>
            <FolderOpen className="h-3.5 w-3.5" />
            Project
          </TabsTrigger>

          <TabsTrigger value="insights" className={triggerCls}>
            <BarChart2 className="h-3.5 w-3.5" />
            Insights
            {hasBaseline && (
              <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-primary border-2 border-muted/70" />
            )}
          </TabsTrigger>

          <TabsTrigger value="grasshopper" className={triggerCls}>
            <Plug className="h-3.5 w-3.5" />
            Grasshopper
          </TabsTrigger>
        </TabsList>

        {/* Right — actions (hidden on Grasshopper tab) */}
        {activeTab !== "grasshopper" && (
          <div className="flex shrink-0 items-center gap-2">
            <Button
              variant="outline" size="sm"
              onClick={commitSave}
              disabled={isSaving || (!hasChanges && !projectId)}
            >
              <Save className="mr-1.5 h-3.5 w-3.5" />
              {isSaving ? "Saving…" : "Save"}
            </Button>
            <Button size="sm" onClick={commitRun} disabled={isRunning} className="gap-1.5">
              <Play className="h-3.5 w-3.5" />
              {isRunning ? "Analysing…" : "Run Analysis"}
            </Button>
          </div>
        )}
      </div>

      {/* ── Project tab ───────────────────────────────────────────────── */}
      <TabsContent value="project" className="flex-1 min-h-0 mt-0">
        <ScrollArea className="h-full">
          <div className="grid gap-6 p-6 max-w-3xl mx-auto">
            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-base"><Building2 className="h-4 w-4" /> Project Information</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Project Name</label>
                  <Input value={localData.project_name} onChange={(e) => { setLocalData((p) => p ? { ...p, project_name: e.target.value } : p); setHasChanges(true) }} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2"><MapPin className="h-3.5 w-3.5" /> Location</label>
                  <Input value={localData.site.location_name || ""} onChange={(e) => { setLocalData((p) => p ? { ...p, site: { ...p.site, location_name: e.target.value || null } } : p); setHasChanges(true) }} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-base"><Layers className="h-4 w-4" /> Design Intent</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 sm:grid-cols-3">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Building Type</label>
                  <Select value={localData.building.building_type || "office"} onValueChange={(v) => { setLocalData((p) => p ? { ...p, building: { ...p.building, building_type: v } } : p); setHasChanges(true) }}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{buildingTypes.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Floors</label>
                  <Input type="number" min={1} value={localData.building.floors ?? 1} onChange={(e) => { setLocalData((p) => p ? { ...p, building: { ...p.building, floors: Number(e.target.value) } } : p); setHasChanges(true) }} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2"><Compass className="h-3.5 w-3.5" /> Orientation</label>
                  <Select value={String(localData.building.orientation_deg ?? 0)} onValueChange={(v) => { setLocalData((p) => p ? { ...p, building: { ...p.building, orientation_deg: Number(v) } } : p); setHasChanges(true) }}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>{orientationChoices.map((o) => <SelectItem key={o} value={String(o)}>{orientationLabels[o]}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {projectId && (
              <Card>
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Layers className="h-4 w-4" /> Floor Plan Analysis
                    <span className="ml-1 text-xs font-normal text-muted-foreground">(optional)</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <FloorPlanUpload projectId={projectId} onAnalysisComplete={(_analysis: FloorPlanAnalysis) => { onStateChange(null); setTimeout(() => onStateChange(localData), 0) }} />
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-base"><Lock className="h-4 w-4" /> Constraints</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Describe your constraints</label>
                    <p className="text-xs text-muted-foreground">Write naturally - the AI will extract hard and soft constraints automatically.</p>
                    <Textarea value={localData.constraints.free_text || ""} onChange={(e) => { setLocalData((p) => p ? { ...p, constraints: { ...p.constraints, free_text: e.target.value, notes: e.target.value ? "Free-text constraints available." : null } } : p); setHasChanges(true) }} placeholder="e.g. Orientation cannot change due to site access. Height capped at 8 floors." className="min-h-[100px]" />
                    <div className="flex items-center gap-3">
                      <Button type="button" variant="outline" size="sm" onClick={handleInterpretConstraints} disabled={isInterpreting || !String(localData.constraints.free_text || "").trim()}>
                        {isInterpreting ? "Interpreting..." : "Interpret"}
                      </Button>
                      <span className="text-xs text-muted-foreground">Mode: {localData.parsed_constraints.parser_mode} · Confidence: {Math.round(localData.parsed_constraints.confidence_score * 100)}%</span>
                    </div>
                    {interpretError && <p className="text-xs text-destructive">{interpretError}</p>}
                  </div>
                  <details>
                    <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground select-none">Advanced — structured hard / soft lists</summary>
                    <div className="mt-3 grid gap-4 sm:grid-cols-2">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Hard constraints</label>
                        <Textarea value={hardConstraintsText} onChange={(e) => handleConstraintChange("hard_constraints", e.target.value)} placeholder="One per line" className="min-h-[80px]" />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Soft constraints</label>
                        <Textarea value={softConstraintsText} onChange={(e) => handleConstraintChange("soft_constraints", e.target.value)} placeholder="One per line" className="min-h-[80px]" />
                      </div>
                    </div>
                  </details>
                  {localData.parsed_constraints.extracted_items.length > 0 && (
                    <div className="space-y-3 rounded-lg border p-3">
                      <div className="text-xs font-semibold text-muted-foreground">Interpreted constraints</div>
                      {localData.parsed_constraints.extracted_items.map((item, index) => (
                        <div key={index} className="rounded-md border p-2">
                          <div className="mb-1 flex items-center justify-between gap-2">
                            <div className="text-sm font-medium">{item.normalized_key}</div>
                            <Badge variant="secondary" className="text-[10px]">{Math.round(item.confidence * 100)}%</Badge>
                          </div>
                          <div className="mb-2 text-xs text-muted-foreground">Source: {item.source_text}</div>
                          <div className="grid gap-2 sm:grid-cols-2">
                            <input className="h-9 rounded-md border px-2 text-sm" value={item.normalized_value == null ? "" : String(item.normalized_value)} onChange={(e) => setParsedItemValue(index, e.target.value)} />
                            <select className="h-9 rounded-md border bg-background px-2 text-sm" value={item.status} onChange={(e) => setParsedItemStatus(index, e.target.value as "proposed" | "accepted" | "rejected" | "edited")}>
                              <option value="proposed">Proposed</option>
                              <option value="accepted">Accepted</option>
                              <option value="edited">Edited</option>
                              <option value="rejected">Rejected</option>
                            </select>
                          </div>
                          {item.rationale && <p className="mt-1 text-xs text-muted-foreground">{item.rationale}</p>}
                        </div>
                      ))}
                    </div>
                  )}
                  {localData.parsed_constraints.conflict_warnings.length > 0 && (
                    <div className="rounded-md border border-amber-300/60 bg-amber-50 p-2 text-xs text-amber-900">
                      <div className="font-medium">Conflict warnings</div>
                      <ul className="mt-1 list-disc pl-4">{localData.parsed_constraints.conflict_warnings.map((v, i) => <li key={i}>{v}</li>)}</ul>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-base"><SlidersHorizontal className="h-4 w-4" /> Priorities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 sm:grid-cols-2">
                  {([
                    { key: "daylight", label: "Daylight" },
                    { key: "energy", label: "Energy Efficiency" },
                    { key: "ventilation", label: "Ventilation" },
                    { key: "cost", label: "Cost" },
                    { key: "aesthetics", label: "Aesthetics" },
                  ] as const).map((p) => (
                    <div key={p.key} className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{p.label}</span>
                        <span className="text-sm font-semibold tabular-nums text-muted-foreground">{(localData.priorities[p.key] * 100).toFixed(0)}%</span>
                      </div>
                      <Slider value={[Math.round(localData.priorities[p.key] * 100)]} onValueChange={(v) => handlePriorityChange(p.key, [Number((v[0] / 100).toFixed(3))])} max={100} step={5} />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {error && <Card className="border-destructive/40"><CardContent className="pt-6 text-sm text-destructive">{error}</CardContent></Card>}

            <div className="flex items-center justify-between rounded-xl border bg-muted/40 p-4">
              <div>
                <p className="text-sm font-medium">Ready to analyse?</p>
                <p className="text-xs text-muted-foreground">Save then run to see environmental scores.</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={commitSave} disabled={isSaving || (!hasChanges && !projectId)}>
                  <Save className="mr-1.5 h-3.5 w-3.5" />{isSaving ? "Saving..." : "Save"}
                </Button>
                <Button size="sm" onClick={commitRun} disabled={isRunning}>
                  <Play className="mr-1.5 h-3.5 w-3.5" />{isRunning ? "Running..." : "Run Analysis"}
                </Button>
              </div>
            </div>
          </div>
        </ScrollArea>
      </TabsContent>

      {/* ── Insights tab ─────────────────────────────────────────────── */}
      <TabsContent value="insights" className="flex-1 min-h-0 mt-0">
        <ScrollArea className="h-full">
          <div className="grid gap-6 p-6 max-w-3xl mx-auto">
            {!hasBaseline ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-16 text-center gap-3">
                  <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center">
                    <Play className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <p className="font-medium">No analysis run yet</p>
                  <p className="text-sm text-muted-foreground max-w-xs">Fill in your project details on the Project tab, then click Run Analysis.</p>
                  <Button size="sm" onClick={() => onTabChange?.("project")} variant="outline" className="mt-2">Go to Project</Button>
                </CardContent>
              </Card>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  {baselineMetrics.map((m) => {
                    const Icon = m.icon
                    return (
                      <Card key={m.label} className="p-4 space-y-2">
                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground"><Icon className="h-3.5 w-3.5" /> {m.label}</div>
                        <div className="text-2xl font-semibold tabular-nums">{m.value.toFixed(0)}<span className="text-sm font-normal text-muted-foreground">%</span></div>
                        <Progress value={m.value} className={cn("h-1.5", m.color)} />
                        <p className="text-[10px] text-muted-foreground">{m.hint}</p>
                      </Card>
                    )
                  })}
                </div>

                {b?.narrative_insight && (
                  <Card className="border-primary/20 bg-primary/5">
                    <CardContent className="flex gap-3 pt-4 pb-4">
                      <Lightbulb className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                      <p className="text-sm leading-relaxed">{b.narrative_insight}</p>
                    </CardContent>
                  </Card>
                )}

                {orientationOptions && (
                  <Card>
                    <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Orientation Options</CardTitle></CardHeader>
                    <CardContent className="pt-0"><OrientationOptions data={orientationOptions} /></CardContent>
                  </Card>
                )}

                {recommendations.length > 0 && (
                  <Card className="border-primary/30 bg-primary/5">
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center gap-2 text-sm font-medium">
                        <Lightbulb className="h-4 w-4 text-primary" /> Top Recommendation
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <h4 className="font-medium">{recommendations[0].title}</h4>
                      <p className="text-sm text-muted-foreground">{recommendations[0].description}</p>
                      <Badge variant="secondary" className="text-xs">score {recommendations[0].score.toFixed(3)}</Badge>
                    </CardContent>
                  </Card>
                )}

                {recommendations.length > 0 && (
                  <Card>
                    <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Trade-offs</CardTitle></CardHeader>
                    <CardContent className="space-y-3">
                      {recommendations.map((opt) => (
                        <div key={opt.title} className="rounded-lg border p-3 space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">{opt.title}</span>
                            <Badge variant="outline" className="text-xs tabular-nums">{opt.score.toFixed(3)}</Badge>
                          </div>
                          <div className="text-xs space-y-1">
                            <p className="text-muted-foreground"><span className="text-foreground">+</span> {opt.expected_benefit}</p>
                            <p className="text-muted-foreground"><span className="text-foreground">-</span> {opt.tradeoff_note}</p>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                <Card>
                  <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">What Changed</CardTitle></CardHeader>
                  <CardContent className="space-y-2">
                    {!diff && <p className="text-sm text-muted-foreground">Run two iterations to view changes.</p>}
                    {diff?.changed_inputs?.slice(0, 5).map((field) => (
                      <div key={field} className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">{field}</span>
                        <Badge variant="outline" className="text-xs">modified</Badge>
                      </div>
                    ))}
                    {diff && Object.keys(diff.changed_baseline_metrics).length > 0 && (
                      <div className="pt-2 text-xs text-muted-foreground">
                        {Object.entries(diff.changed_baseline_metrics).map(([key, values]) => (
                          <div key={key} className="mt-1 flex items-center gap-1.5">
                            <span>{key}</span><ArrowRight className="h-3 w-3" />
                            <span>{String(values.previous)}</span><ArrowRight className="h-3 w-3" />
                            <span className="font-medium text-foreground">{String(values.current)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {run && <div className="pt-2 text-xs text-muted-foreground">Run: {new Date(run.created_at).toLocaleString()} | Provider: {run.climate_provider || "n/a"}</div>}
                    {review?.top_option_reason && <div className="rounded-md border p-2 text-xs text-muted-foreground">{review.top_option_reason}</div>}
                    {review?.penalty_summary && <div className="rounded-md border p-2 text-xs text-muted-foreground">{review.penalty_summary}</div>}
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </ScrollArea>
      </TabsContent>

      {/* ── Grasshopper tab ──────────────────────────────────────────── */}
      <TabsContent value="grasshopper" className="flex-1 min-h-0 mt-0">
        <GrasshopperPanel />
      </TabsContent>

    </Tabs>
  )
}
