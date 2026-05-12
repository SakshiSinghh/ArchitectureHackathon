"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Plug, Sliders, ToggleRight, Terminal, Lightbulb, ChevronRight, Download } from "lucide-react"

const STEPS = [
  {
    icon: Terminal,
    title: "Start the backend",
    content: "Open a terminal in the project folder and run:",
    code: "uvicorn backend.main:app --reload --port 8000",
  },
  {
    icon: Download,
    title: "Download the component",
    content: "Use the Download button in the top bar. Save the .py file somewhere you can find it.",
    code: null,
  },
  {
    icon: Plug,
    title: "Add a GHPython component",
    content: "In Grasshopper: double-click the canvas, search for Python 3 Script (Rhino 8) or GHPython (Rhino 7). Drop it on the canvas.",
    code: null,
  },
  {
    icon: Sliders,
    title: "Add inputs",
    content: "Right-click the component → Inputs, add these four params:",
    code: "orientation_deg  (float)\nlocation         (str)\nbuilding_type    (str)\nrun              (bool)",
  },
  {
    icon: Sliders,
    title: "Add outputs",
    content: "Right-click the component → Outputs, add these params:",
    code: "energy_risk\ndaylight_potential\nventilation_potential\nbest_orientation\nbest_score\nnarrative\nall_options",
  },
  {
    icon: Plug,
    title: "Paste the script",
    content: "Double-click the component to open the editor. Select all, delete, then paste the downloaded script. Close the editor.",
    code: null,
  },
  {
    icon: Sliders,
    title: "Wire up inputs",
    content: "Connect components to the inputs:",
    code: "Number Slider (0-360)  →  orientation_deg\nPanel with city name   →  location\nPanel with type        →  building_type\nBoolean Toggle         →  run",
  },
  {
    icon: ToggleRight,
    title: "Run it",
    content: "Right-click the Boolean Toggle and set to True. Scores and ranked orientation options appear instantly.",
    code: null,
  },
]

const INPUTS = [
  { name: "orientation_deg", type: "float", example: "90", note: "0 = North, 90 = East, 180 = South, 270 = West" },
  { name: "location", type: "str", example: "Pune", note: "City name used for climate data lookup" },
  { name: "building_type", type: "str", example: "office", note: "office / residential / mixed_use" },
  { name: "run", type: "bool", example: "True", note: "Toggle to True to fire the backend request" },
]

const OUTPUTS = [
  { name: "energy_risk", note: "0–1 score for current orientation" },
  { name: "daylight_potential", note: "0–1 score for current orientation" },
  { name: "ventilation_potential", note: "0–1 score for current orientation" },
  { name: "best_orientation", note: "Label of top-ranked orientation e.g. South-East" },
  { name: "best_score", note: "Composite score of the best option" },
  { name: "narrative", note: "One-sentence insight for the top option" },
  { name: "all_options", note: "Formatted text of all 3 ranked options with scores" },
]

export function GrasshopperPanel() {
  return (
    <ScrollArea className="h-full">
      <div className="space-y-5 p-6 max-w-3xl mx-auto">

        {/* Overview */}
        <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>
                A single GHPython component that calls the ArchEnv backend from your Grasshopper canvas.
                Drag an orientation slider and get energy, daylight, and ventilation scores — plus 3 ranked
                orientation options with narratives — without leaving Rhino.
              </p>
              <div className="flex flex-wrap gap-2 pt-1">
                <Badge variant="secondary">Rhino 7 (IronPython)</Badge>
                <Badge variant="secondary">Rhino 8 (CPython)</Badge>
                <Badge variant="secondary">No plugins needed</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Setup steps — collapsible */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">Setup — 8 steps</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 pb-4">
              {STEPS.map((step, i) => {
                const Icon = step.icon
                return (
                  <details key={i} className="group rounded-lg border overflow-hidden">
                    <summary className="flex cursor-pointer select-none list-none items-center justify-between gap-3 p-3 text-sm font-medium hover:bg-muted/50 transition-colors duration-150 [&::-webkit-details-marker]:hidden">
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[10px] font-bold text-primary">
                          {i + 1}
                        </span>
                        <Icon className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                        <span className="truncate">{step.title}</span>
                      </div>
                      <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 group-open:rotate-90" />
                    </summary>
                    <div className="border-t px-4 pb-4 pt-3 space-y-2">
                      <p className="text-xs text-muted-foreground leading-relaxed">{step.content}</p>
                      {step.code && (
                        <pre className="rounded-md bg-muted px-3 py-2.5 text-xs font-mono whitespace-pre-wrap leading-relaxed">{step.code}</pre>
                      )}
                    </div>
                  </details>
                )
              })}
            </CardContent>
          </Card>

          {/* Input reference */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">Inputs</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {INPUTS.map((inp) => (
                <div key={inp.name} className="rounded-md bg-muted/50 p-2.5 space-y-1">
                  <div className="flex items-center gap-2">
                    <code className="text-xs font-mono font-semibold">{inp.name}</code>
                    <Badge variant="outline" className="h-4 px-1 text-[10px]">{inp.type}</Badge>
                    <span className="text-[10px] text-muted-foreground">e.g. {inp.example}</span>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">{inp.note}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Output reference */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">Outputs</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {OUTPUTS.map((out) => (
                <div key={out.name} className="rounded-md bg-muted/50 p-2.5 space-y-1">
                  <code className="text-xs font-mono font-semibold block">{out.name}</code>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">{out.note}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Tip */}
          <Card className="border-primary/20 bg-primary/5">
            <CardContent className="flex gap-2.5 pt-4 pb-4">
              <Lightbulb className="h-4 w-4 text-primary shrink-0 mt-0.5" />
              <p className="text-xs text-muted-foreground leading-relaxed">
                <span className="font-medium text-foreground">Tip: </span>
                Works without a Claude API key using heuristic scoring. Add{" "}
                <code className="rounded bg-muted px-1">ANTHROPIC_API_KEY</code> to{" "}
                <code className="rounded bg-muted px-1">.env</code> for AI-written narrative insights.
              </p>
            </CardContent>
          </Card>

      </div>
    </ScrollArea>
  )
}
