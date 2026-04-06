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
import type { AgentReviewResponse, ProjectState, RunDiff, RunSnapshot } from "@/lib/api-types"

type RightPanelProps = {
  state: ProjectState | null
  review: AgentReviewResponse | null
  diff: RunDiff | null
  run: RunSnapshot | null
}

function numeric(value: unknown): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

export function RightPanel({ state, review, diff, run }: RightPanelProps) {
  const climateMetrics = (state?.climate_context?.environmental_metrics as Record<string, unknown>) || {}

  const baselineMetrics = [
    {
      label: "Heat Exposure",
      value: numeric(climateMetrics.heat_exposure_score) * 100,
      unit: "%",
      icon: Thermometer,
      status: "warning",
    },
    {
      label: "Solar Exposure",
      value: numeric(climateMetrics.solar_exposure_score) * 100,
      unit: "%",
      icon: Sun,
      status: "good",
    },
    {
      label: "Ventilation Potential",
      value: numeric(climateMetrics.ventilation_potential_score) * 100,
      unit: "%",
      icon: Wind,
      status: "moderate",
    },
  ]

  const recommendations = review?.ranked_options || []

  return (
    <div className="flex h-full w-80 flex-col border-l bg-sidebar">
      {/* Header */}
      <div className="flex h-16 items-center border-b px-4">
        <h2 className="font-semibold">Insights</h2>
      </div>

      <ScrollArea className="flex-1">
        <div className="space-y-4 p-4">
          {/* Baseline Metrics */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">
                Baseline Metrics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {baselineMetrics.map((metric) => {
                const Icon = metric.icon
                return (
                  <div key={metric.label} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">{metric.label}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm font-semibold">
                          {metric.value.toFixed(1)}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {metric.unit}
                        </span>
                      </div>
                    </div>
                    <Progress
                      value={metric.value}
                      className={cn(
                        "h-1.5",
                        metric.status === "good" && "[&>div]:bg-accent",
                        metric.status === "warning" && "[&>div]:bg-orange-500",
                        metric.status === "moderate" && "[&>div]:bg-yellow-500"
                      )}
                    />
                  </div>
                )
              })}
            </CardContent>
          </Card>

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
