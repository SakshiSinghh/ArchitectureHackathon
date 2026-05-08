"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Thermometer, Sun, Wind, Star } from "lucide-react"
import { cn } from "@/lib/utils"
import { OrientationDiagram } from "./orientation-diagram"
import type { OrientationOptionsResponse } from "@/lib/api-types"

type Props = {
  data: OrientationOptionsResponse
  onSelect?: (deg: number) => void
}

function ScoreBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="h-1 w-full rounded-full bg-muted overflow-hidden">
      <div
        className={cn("h-full rounded-full transition-all", color)}
        style={{ width: `${Math.round(value * 100)}%` }}
      />
    </div>
  )
}

export function OrientationOptions({ data, onSelect }: Props) {
  const { options, recommended_orientation_deg, location } = data

  return (
    <div className="space-y-3">
      {location ? (
        <p className="text-xs text-muted-foreground">
          Ranked for <span className="font-medium text-foreground">{location}</span>
        </p>
      ) : null}

      <div className="space-y-2">
        {options.map((opt) => {
          const isTop = opt.orientation_deg === recommended_orientation_deg && opt.rank === 1
          return (
            <Card
              key={opt.orientation_deg}
              className={cn(
                "cursor-pointer transition-colors hover:border-accent/60",
                isTop && "border-accent/50 bg-accent/5",
                opt.is_current && !isTop && "border-blue-300/60 bg-blue-50/30 dark:bg-blue-950/20"
              )}
              onClick={() => onSelect?.(opt.orientation_deg)}
            >
              <CardHeader className="pb-2 pt-3 px-3">
                <CardTitle className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    {isTop ? (
                      <Badge className="h-5 px-1.5 text-xs bg-accent text-accent-foreground gap-1">
                        <Star className="h-3 w-3" /> #1
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="h-5 px-1.5 text-xs tabular-nums">
                        #{opt.rank}
                      </Badge>
                    )}
                    <span className="font-semibold">{opt.label}</span>
                    <span className="text-xs text-muted-foreground font-normal">
                      {opt.orientation_deg.toFixed(0)}&deg;
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    {opt.is_current && (
                      <Badge variant="secondary" className="h-5 px-1.5 text-xs">
                        Current
                      </Badge>
                    )}
                    <span className="text-xs tabular-nums text-muted-foreground">
                      {opt.composite_score.toFixed(3)}
                    </span>
                  </div>
                </CardTitle>
              </CardHeader>

              <CardContent className="px-3 pb-3 space-y-2">
                <div className="flex gap-3 items-start">
                  <div className="shrink-0">
                    <OrientationDiagram orientationDeg={opt.orientation_deg} size={80} />
                  </div>

                  <div className="flex-1 min-w-0 space-y-2 pt-1">
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="flex items-center gap-1 text-muted-foreground">
                          <Thermometer className="h-3 w-3" /> Energy risk
                        </span>
                        <span className="tabular-nums">{(opt.energy_risk * 100).toFixed(0)}%</span>
                      </div>
                      <ScoreBar value={opt.energy_risk} color="bg-orange-500" />
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="flex items-center gap-1 text-muted-foreground">
                          <Sun className="h-3 w-3" /> Daylight
                        </span>
                        <span className="tabular-nums">{(opt.daylight_potential * 100).toFixed(0)}%</span>
                      </div>
                      <ScoreBar value={opt.daylight_potential} color="bg-yellow-400" />
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="flex items-center gap-1 text-muted-foreground">
                          <Wind className="h-3 w-3" /> Ventilation
                        </span>
                        <span className="tabular-nums">{(opt.ventilation_potential * 100).toFixed(0)}%</span>
                      </div>
                      <ScoreBar value={opt.ventilation_potential} color="bg-sky-400" />
                    </div>
                  </div>
                </div>

                <p className="text-xs text-muted-foreground leading-relaxed border-t pt-2">
                  {opt.narrative}
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
