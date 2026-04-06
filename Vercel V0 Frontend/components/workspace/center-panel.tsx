"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useOnboarding, type ProjectData } from "@/lib/onboarding-context"
import { Save, Play, Layers, Lock, SlidersHorizontal, Compass, Building2, MapPin } from "lucide-react"
import { cn } from "@/lib/utils"

const buildingTypes = [
  { value: "residential", label: "Residential" },
  { value: "office", label: "Office" },
  { value: "mixed-use", label: "Mixed-Use" },
  { value: "retail", label: "Retail" },
  { value: "hospitality", label: "Hospitality" },
]

const scales = [
  { value: "low-rise", label: "Low-rise" },
  { value: "mid-rise", label: "Mid-rise" },
  { value: "high-rise", label: "High-rise" },
]

const orientations = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

export function CenterPanel() {
  const { projectData, updateProjectData } = useOnboarding()
  const [localData, setLocalData] = useState<ProjectData>(projectData)
  const [hasChanges, setHasChanges] = useState(false)

  const handleChange = <K extends keyof ProjectData>(
    key: K,
    value: ProjectData[K]
  ) => {
    setLocalData((prev) => ({ ...prev, [key]: value }))
    setHasChanges(true)
  }

  const handleConstraintChange = (key: keyof ProjectData["constraints"]) => {
    setLocalData((prev) => ({
      ...prev,
      constraints: { ...prev.constraints, [key]: !prev.constraints[key] },
    }))
    setHasChanges(true)
  }

  const handlePriorityChange = (
    key: keyof ProjectData["priorities"],
    value: number[]
  ) => {
    setLocalData((prev) => ({
      ...prev,
      priorities: { ...prev.priorities, [key]: value[0] },
    }))
    setHasChanges(true)
  }

  const handleSave = () => {
    updateProjectData(localData)
    setHasChanges(false)
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b px-6">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-semibold">{localData.name}</h1>
          {hasChanges && (
            <Badge variant="secondary" className="text-xs">
              Unsaved changes
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={handleSave} disabled={!hasChanges}>
            <Save className="mr-2 h-4 w-4" />
            Save
          </Button>
          <Button>
            <Play className="mr-2 h-4 w-4" />
            Run Analysis
          </Button>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="grid gap-6 p-6">
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
                  value={localData.name}
                  onChange={(e) => handleChange("name", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <MapPin className="h-3.5 w-3.5" />
                  Location
                </label>
                <Input
                  value={localData.location}
                  onChange={(e) => handleChange("location", e.target.value)}
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
                  value={localData.buildingType}
                  onValueChange={(value) => handleChange("buildingType", value)}
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
                <label className="text-sm font-medium">Scale</label>
                <Select
                  value={localData.scale}
                  onValueChange={(value) => handleChange("scale", value)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {scales.map((s) => (
                      <SelectItem key={s.value} value={s.value}>
                        {s.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Compass className="h-3.5 w-3.5" />
                  Orientation
                </label>
                <Select
                  value={localData.orientation}
                  onValueChange={(value) => handleChange("orientation", value)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {orientations.map((o) => (
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
              <div className="grid gap-4 sm:grid-cols-3">
                {(
                  [
                    { key: "lockOrientation", label: "Lock Orientation" },
                    { key: "lockFacade", label: "Lock Facade" },
                    { key: "heightRestriction", label: "Height Restriction" },
                  ] as const
                ).map((constraint) => (
                  <div
                    key={constraint.key}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <span className="text-sm font-medium">{constraint.label}</span>
                    <Switch
                      checked={localData.constraints[constraint.key]}
                      onCheckedChange={() =>
                        handleConstraintChange(constraint.key)
                      }
                    />
                  </div>
                ))}
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
                    { key: "energyEfficiency", label: "Energy Efficiency" },
                    { key: "cost", label: "Cost" },
                    { key: "aesthetics", label: "Aesthetics" },
                  ] as const
                ).map((priority) => (
                  <div key={priority.key} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{priority.label}</span>
                      <span className="text-sm font-semibold tabular-nums text-muted-foreground">
                        {localData.priorities[priority.key]}%
                      </span>
                    </div>
                    <Slider
                      value={[localData.priorities[priority.key]]}
                      onValueChange={(value) =>
                        handlePriorityChange(priority.key, value)
                      }
                      max={100}
                      step={5}
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </ScrollArea>
    </div>
  )
}
