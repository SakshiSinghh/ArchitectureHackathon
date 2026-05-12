"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Progress } from "@/components/ui/progress"
import {
  Thermometer,
  Sun,
  Wind,
  Lightbulb,
  ArrowRight,
} from "lucide-react"
import { cn } from "@/lib/utils"
import type { AgentReviewResponse, OrientationOptionsResponse, ProjectState, RunDiff, RunSnapshot } from "@/lib/api-types"
import { OrientationOptions } from "./orientation-options"

type RightPanelProps = {
  state: ProjectState | null
  review: AgentReviewResponse | null
  diff: RunDiff | null
  run: RunSnapshot | null
  orientationOptions: OrientationOptionsResponse | null
}

function numeric(value: unknown): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

export function RightPanel({ state, review, diff, run, orientationOptions }: RightPanelProps) {
  const b = state?.baseline_results

  const hasBaseline = b && (
    b.energy_risk != null ||
    b.daylight_potential != null ||
    b.ventilation_potential != null
  )

  const baselineMetrics = [
    {
      label: "Energy Risk",
      value: numeric(b?.energy_risk) * 100,
      unit: "%",
      icon: Thermometer,
      color: "[&>div]:bg-orange-500",
      hint: "Lower is better",
    },
    {
      label: "Daylight Potential",
      value: numeric(b?.daylight_potential) * 100,
      unit: "%",
      icon: Sun,
      color: "[&>div]:bg-yellow-400",
      hint: "Higher is better",
    },
    {
      label: "Ventilation",
      value: numeric(b?.ventilation_potential) * 100,
      unit: "%",
      icon: Wind,
      color: "[&>div]:bg-sky-400",
      hint: "Higher is better",
    },
    {
      label: "Heat Exposure",
      value: numeric(b?.heat_exposure_score) * 100,
      unit: "%",
      icon: Thermometer,
      color: "[&>div]:bg-red-400",
      hint: "Lower is better",
    },
  ]

  const recommendations = review?.ranked_options || []

  return (
    <div className="flex h-full w-96 shrink-0 flex-col border-l bg-sidebar overflow-hidden">
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b px-4">
        <div>
          <h2 className="font-semibold">Insights</h2>
          <p className="text-xs text-muted-foreground">Environmental analysis</p>
        </div>
      </div>

      <ScrollArea className="flex-1 min-h-0">
        <div className="space-y-4 p-4">
          {/* Baseline Metrics */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Baseline Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!hasBaseline ? (
                <div className="rounded-lg bg-muted/50 p-4 text-center space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">No analysis yet</p>
                  <p className="text-xs text-muted-foreground">Fill in your project details and click Run Analysis</p>
                </div>
              ) : (
                baselineMetrics.map((metric) => {
                  const Icon = metric.icon
                  return (
                    <div key={metric.label} className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Icon className="h-3.5 w-3.5 text-muted-foreground" />
                          <span className="text-sm">{metric.label}</span>
                          <span className="text-xs text-muted-foreground">({metric.hint})</span>
                        </div>
                        <span className="text-sm font-semibold tabular-nums">
                          {metric.value.toFixed(0)}{metric.unit}
                        </span>
                      </div>
                      <Progress value={metric.value} className={cn("h-1.5", metric.color)} />
                    </div>
                  )
                })
              )}
              {hasBaseline && b?.narrative_insight && (
                <p className="text-xs text-muted-foreground border-t pt-3 leading-relaxed">
                  {b.narrative_insight}
                </p>
              )}
            </CardContent>
          </Card>

          {/* Orientation Options */}
          {orientationOptions && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Orientation Options</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <OrientationOptions data={orientationOptions} />
              </CardContent>
            </Card>
          )}

          {/* Top Recommendation */}
          <Card className="border-accent/50 bg-accent/5">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Lightbulb className="h-4 w-4 text-accent" />
                Top Recommendation
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recommendations.length === 0 ? (
                <p className="text-sm text-muted-foreground">Run analysis to see recommendations.</p>
              ) : null}
              {recommendations.slice(0, 1).map((rec, index) => (
                <div key={index} className="space-y-2">
                  <h4 className="font-medium">{rec.title}</h4>
                  <p className="text-sm text-muted-foreground">
                    {rec.description}
                  </p>
                  <Badge variant="secondary" className="text-xs">
                    score {rec.score.toFixed(3)}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Trade-offs */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Trade-offs</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {recommendations.length === 0 ? <p className="text-sm text-muted-foreground">No trade-off data yet.</p> : null}
              {recommendations.map((option) => (
                <div
                  key={option.title}
                  className="rounded-lg border p-3 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{option.title}</span>
                    <Badge variant="outline" className="text-xs tabular-nums">
                      {option.score.toFixed(3)}
                    </Badge>
                  </div>
                  <div className="text-xs space-y-1">
                    <p className="text-muted-foreground">
                      <span className="text-foreground">+</span> {option.expected_benefit}
                    </p>
                    <p className="text-muted-foreground">
                      <span className="text-foreground">−</span> {option.tradeoff_note}
                    </p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* What Changed */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">What Changed</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {!diff ? <p className="text-sm text-muted-foreground">Run two iterations to view changes.</p> : null}
              {diff?.changed_inputs?.slice(0, 5).map((field) => (
                <div key={field} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{field}</span>
                  <Badge variant="outline" className="text-xs">
                    modified
                  </Badge>
                </div>
              ))}
              {diff && Object.keys(diff.changed_baseline_metrics).length > 0 ? (
                <div className="pt-2 text-xs text-muted-foreground">
                  Baseline metric changes:
                  {Object.entries(diff.changed_baseline_metrics).map(([key, values]) => (
                    <div key={key} className="mt-1 flex items-center gap-1.5">
                      <span>{key}</span>
                      <ArrowRight className="h-3 w-3" />
                      <span>{String(values.previous)}</span>
                      <ArrowRight className="h-3 w-3" />
                      <span className="font-medium text-foreground">{String(values.current)}</span>
                    </div>
                  ))}
                </div>
              ) : null}
              {run ? (
                <div className="pt-2 text-xs text-muted-foreground">
                  Run: {new Date(run.created_at).toLocaleString()} | Provider: {run.climate_provider || "n/a"}
                </div>
              ) : null}
              {review?.top_option_reason ? (
                <div className="rounded-md border p-2 text-xs text-muted-foreground">{review.top_option_reason}</div>
              ) : null}
              {review?.penalty_summary ? (
                <div className="rounded-md border p-2 text-xs text-muted-foreground">{review.penalty_summary}</div>
              ) : null}
            </CardContent>
          </Card>
        </div>
      </ScrollArea>
    </div>
  )
}
