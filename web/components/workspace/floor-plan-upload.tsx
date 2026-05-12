"use client"

import { useRef, useState } from "react"
import { uploadFloorPlan } from "@/lib/api-client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { FileUp, Loader2, AlertCircle, ChevronDown, ChevronUp, CheckCircle2 } from "lucide-react"
import type { FloorPlanAnalysis } from "@/lib/api-types"

type Props = {
  projectId: string
  onAnalysisComplete: (analysis: FloorPlanAnalysis) => void
}

const CONFIDENCE_COLORS: Record<string, string> = {
  high: "bg-green-100 text-green-800 border-green-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  low: "bg-gray-100 text-gray-600 border-gray-200",
}

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif", "application/pdf"]

export function FloorPlanUpload({ projectId, onAnalysisComplete }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<FloorPlanAnalysis | null>(null)
  const [expandedRooms, setExpandedRooms] = useState<Set<number>>(new Set())
  const [fileName, setFileName] = useState<string | null>(null)

  const handleFile = async (file: File) => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError("Unsupported file type. Upload a JPEG, PNG, WebP, GIF, or PDF.")
      return
    }
    setError(null)
    setIsUploading(true)
    setFileName(file.name)
    try {
      const result = await uploadFloorPlan(projectId, file)
      setAnalysis(result.floor_plan_analysis)
      onAnalysisComplete(result.floor_plan_analysis)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed")
    } finally {
      setIsUploading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  const toggleRoom = (i: number) => {
    setExpandedRooms((prev) => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })
  }

  return (
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-base">
          <FileUp className="h-4 w-4" />
          Review Mode - Floor Plan Upload
        </CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div
          className="flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed border-muted-foreground/25 px-6 py-8 text-center transition-colors hover:border-muted-foreground/50 cursor-pointer"
          onClick={() => inputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          {isUploading ? (
            <>
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Analysing {fileName}...</p>
            </>
          ) : (
            <>
              <FileUp className="h-8 w-8 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Drop floor plan here or click to browse</p>
                <p className="text-xs text-muted-foreground mt-1">JPEG, PNG, WebP, GIF, PDF</p>
              </div>
              {fileName && !analysis && (
                <Badge variant="outline" className="text-xs">{fileName}</Badge>
              )}
            </>
          )}
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif,application/pdf"
          className="hidden"
          onChange={handleInputChange}
        />

        {error && (
          <div className="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
            {error}
          </div>
        )}

        {analysis && (
          <div className="grid gap-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium">{fileName}</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className={CONFIDENCE_COLORS[analysis.confidence]}>
                  {analysis.confidence} confidence
                </Badge>
                {analysis.primary_orientation_deg != null && (
                  <Badge variant="outline">{analysis.primary_orientation_deg} deg orientation</Badge>
                )}
              </div>
            </div>

            <p className="text-xs text-muted-foreground">{analysis.north_assumption}</p>

            {analysis.overall_issues.length > 0 && (
              <div className="rounded-md border border-orange-200 bg-orange-50 p-3 grid gap-1">
                <p className="text-xs font-semibold text-orange-800">Issues identified</p>
                <ul className="grid gap-0.5">
                  {analysis.overall_issues.map((issue, i) => (
                    <li key={i} className="text-xs text-orange-700 flex gap-1.5">
                      <span className="mt-0.5">-</span>{issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {analysis.overall_suggestions.length > 0 && (
              <div className="rounded-md border border-blue-200 bg-blue-50 p-3 grid gap-1">
                <p className="text-xs font-semibold text-blue-800">Recommendations</p>
                <ul className="grid gap-0.5">
                  {analysis.overall_suggestions.map((s, i) => (
                    <li key={i} className="text-xs text-blue-700 flex gap-1.5">
                      <span className="mt-0.5">-</span>{s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {analysis.rooms.length > 0 && (
              <div className="grid gap-1.5">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Room breakdown</p>
                {analysis.rooms.map((room, i) => (
                  <div key={i} className="rounded-md border text-sm">
                    <button
                      className="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-muted/50 transition-colors"
                      onClick={() => toggleRoom(i)}
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{room.room_name}</span>
                        {room.facade_orientations.length > 0 && (
                          <span className="text-xs text-muted-foreground">
                            {room.facade_orientations.join(", ")}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        {room.environmental_issues.length > 0 && (
                          <Badge variant="outline" className="text-xs bg-orange-50 text-orange-700 border-orange-200">
                            {room.environmental_issues.length} issue{room.environmental_issues.length !== 1 ? "s" : ""}
                          </Badge>
                        )}
                        {expandedRooms.has(i) ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                      </div>
                    </button>
                    {expandedRooms.has(i) && (
                      <div className="border-t px-3 py-2 grid gap-2">
                        {room.environmental_issues.length > 0 && (
                          <div>
                            <p className="text-xs font-medium text-orange-700 mb-1">Issues</p>
                            <ul className="grid gap-0.5">
                              {room.environmental_issues.map((issue, j) => (
                                <li key={j} className="text-xs text-muted-foreground flex gap-1.5">
                                  <span>-</span>{issue}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {room.suggestions.length > 0 && (
                          <div>
                            <p className="text-xs font-medium text-blue-700 mb-1">Suggestions</p>
                            <ul className="grid gap-0.5">
                              {room.suggestions.map((s, j) => (
                                <li key={j} className="text-xs text-muted-foreground flex gap-1.5">
                                  <span>-</span>{s}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            <Button
              variant="outline"
              size="sm"
              className="w-fit"
              onClick={() => { setAnalysis(null); setFileName(null); inputRef.current?.click() }}
            >
              Upload another plan
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
