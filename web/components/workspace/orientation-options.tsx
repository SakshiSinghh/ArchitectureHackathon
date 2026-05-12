"use client"

import { cn } from "@/lib/utils"
import type { OrientationOptionsResponse } from "@/lib/api-types"
import { Star, MapPin } from "lucide-react"
import { Badge } from "@/components/ui/badge"

type Props = { data: OrientationOptionsResponse }

function MiniBar({ value, colorClass }: { value: number; colorClass: string }) {
  return (
    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
      <div
        className={cn("h-full rounded-full transition-all", colorClass)}
        style={{ width: `${Math.min(Math.max(value, 0), 100)}%` }}
      />
    </div>
  )
}

export function OrientationOptions({ data }: Props) {
  const options = data.options ?? []

  return (
    <div className="space-y-2.5">
      {data.location && (
        <p className="flex items-center gap-1.5 text-xs text-muted-foreground pb-1">
          <MapPin className="h-3 w-3" />
          Ranked for <span className="font-medium text-foreground">{data.location}</span>
        </p>
      )}

      {options.map((opt) => {
        const isTop = opt.rank === 1
        const isCurrent = opt.is_current && !isTop

        return (
          <div
            key={opt.orientation_deg}
            className={cn(
              "rounded-xl border p-4 space-y-3 transition-all",
              isTop  && "border-primary/30 bg-primary/5 shadow-sm",
              isCurrent && "border-border bg-muted/40",
              !isTop && !isCurrent && "border-border/50 opacity-75"
            )}
          >
            {/* Header row */}
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2.5 min-w-0">
                {isTop ? (
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary">
                    <Star className="h-3 w-3 fill-primary-foreground text-primary-foreground" />
                  </span>
                ) : (
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-semibold text-muted-foreground">
                    {opt.rank}
                  </span>
                )}
                <span className="text-sm font-semibold truncate">{opt.label}</span>
                <span className="text-xs text-muted-foreground shrink-0">{opt.orientation_deg}°</span>
                {isTop  && <Badge className="shrink-0 h-5 px-1.5 text-[10px] bg-primary text-primary-foreground">Best</Badge>}
                {isCurrent && <Badge variant="outline" className="shrink-0 h-5 px-1.5 text-[10px]">Current</Badge>}
              </div>
              <span className="text-sm font-semibold tabular-nums text-muted-foreground shrink-0">
                {opt.composite_score.toFixed(3)}
              </span>
            </div>

            {/* Metric bars */}
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                  <span>Energy risk</span>
                  <span className="tabular-nums">{(opt.energy_risk * 100).toFixed(0)}%</span>
                </div>
                <MiniBar value={opt.energy_risk * 100} colorClass="bg-orange-400" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                  <span>Daylight</span>
                  <span className="tabular-nums">{(opt.daylight_potential * 100).toFixed(0)}%</span>
                </div>
                <MiniBar value={opt.daylight_potential * 100} colorClass="bg-yellow-400" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                  <span>Ventilation</span>
                  <span className="tabular-nums">{(opt.ventilation_potential * 100).toFixed(0)}%</span>
                </div>
                <MiniBar value={opt.ventilation_potential * 100} colorClass="bg-sky-400" />
              </div>
            </div>

            {/* Narrative — only on top pick */}
            {opt.narrative && isTop && (
              <p className="text-xs text-muted-foreground leading-relaxed border-t border-border/60 pt-2.5">
                {opt.narrative}
              </p>
            )}
          </div>
        )
      })}
    </div>
  )
}
