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
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react"
import { cn } from "@/lib/utils"

const baselineMetrics = [
  {
    label: "Heat Exposure",
    value: 72,
    unit: "kWh/m²",
    icon: Thermometer,
    status: "warning",
    trend: "up",
  },
  {
    label: "Solar Exposure",
    value: 4.2,
    unit: "hours/day",
    icon: Sun,
    status: "good",
    trend: "neutral",
  },
  {
    label: "Ventilation Potential",
    value: 65,
    unit: "%",
    icon: Wind,
    status: "moderate",
    trend: "down",
  },
]

const recommendations = [
  {
    title: "Rotate building 15° clockwise",
    description:
      "This adjustment would reduce heat exposure by 12% while maintaining optimal daylight.",
    impact: "+8% efficiency",
  },
]

const tradeoffs = [
  {
    option: "Maximize daylight",
    pros: "Better occupant comfort, reduced lighting costs",
    cons: "Higher cooling load in summer",
    score: 85,
  },
  {
    option: "Minimize energy use",
    pros: "Lower operational costs, better sustainability rating",
    cons: "May require smaller windows",
    score: 78,
  },
  {
    option: "Balance approach",
    pros: "Good compromise across all metrics",
    cons: "No metric is fully optimized",
    score: 82,
  },
]

const changes = [
  { field: "Orientation", from: "N", to: "NNE", type: "modified" },
  { field: "Window ratio", from: "40%", to: "35%", type: "modified" },
  { field: "Shading depth", from: "0.5m", to: "0.8m", type: "added" },
]

export function RightPanel() {
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
                          {metric.value}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {metric.unit}
                        </span>
                        {metric.trend === "up" && (
                          <TrendingUp className="h-3 w-3 text-destructive" />
                        )}
                        {metric.trend === "down" && (
                          <TrendingDown className="h-3 w-3 text-accent" />
                        )}
                        {metric.trend === "neutral" && (
                          <Minus className="h-3 w-3 text-muted-foreground" />
                        )}
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
              {recommendations.map((rec, index) => (
                <div key={index} className="space-y-2">
                  <h4 className="font-medium">{rec.title}</h4>
                  <p className="text-sm text-muted-foreground">
                    {rec.description}
                  </p>
                  <Badge variant="secondary" className="text-xs">
                    {rec.impact}
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
              {tradeoffs.map((option) => (
                <div
                  key={option.option}
                  className="rounded-lg border p-3 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{option.option}</span>
                    <Badge variant="outline" className="text-xs tabular-nums">
                      {option.score}
                    </Badge>
                  </div>
                  <div className="text-xs space-y-1">
                    <p className="text-muted-foreground">
                      <span className="text-foreground">+</span> {option.pros}
                    </p>
                    <p className="text-muted-foreground">
                      <span className="text-foreground">−</span> {option.cons}
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
              {changes.map((change) => (
                <div
                  key={change.field}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-muted-foreground">{change.field}</span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-muted-foreground">{change.from}</span>
                    <ArrowRight className="h-3 w-3 text-muted-foreground" />
                    <span className="font-medium">{change.to}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </ScrollArea>
    </div>
  )
}
