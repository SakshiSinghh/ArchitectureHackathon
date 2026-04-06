"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { Plus, FolderOpen, Clock, ChevronRight } from "lucide-react"
import { useOnboarding } from "@/lib/onboarding-context"

type Project = {
  id: string
  name: string
  lastModified: string
  iterations: number
}

const mockProjects: Project[] = [
  { id: "1", name: "Current Project", lastModified: "Just now", iterations: 1 },
]

const mockHistory = [
  { id: "1", label: "Baseline Analysis", timestamp: "Just now" },
]

export function LeftSidebar() {
  const [activeProject, setActiveProject] = useState("1")
  const { projectData, resetOnboarding } = useOnboarding()

  const projects = [
    { ...mockProjects[0], name: projectData.name || "Current Project" },
  ]

  return (
    <div className="flex h-full w-64 flex-col border-r bg-sidebar">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <span className="text-sm font-bold text-primary-foreground">F</span>
        </div>
        <span className="text-lg font-semibold">Formscape</span>
      </div>

      {/* New Project Button */}
      <div className="p-4">
        <Button 
          className="w-full gap-2" 
          variant="outline"
          onClick={resetOnboarding}
        >
          <Plus className="h-4 w-4" />
          New Project
        </Button>
      </div>

      {/* Projects Section */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="px-4 pb-4">
            <div className="mb-2 flex items-center gap-2 text-xs font-medium text-muted-foreground">
              <FolderOpen className="h-3.5 w-3.5" />
              PROJECTS
            </div>
            <div className="space-y-1">
              {projects.map((project) => (
                <button
                  key={project.id}
                  onClick={() => setActiveProject(project.id)}
                  className={cn(
                    "flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition-colors",
                    activeProject === project.id
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "hover:bg-sidebar-accent/50"
                  )}
                >
                  <div className="min-w-0 flex-1">
                    <div className="truncate font-medium">{project.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {project.lastModified}
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
                </button>
              ))}
            </div>
          </div>

          {/* Run History */}
          <div className="px-4 pb-4">
            <div className="mb-2 flex items-center gap-2 text-xs font-medium text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              RUN HISTORY
            </div>
            <div className="space-y-1">
              {mockHistory.map((run) => (
                <div
                  key={run.id}
                  className="flex items-center justify-between rounded-lg px-3 py-2 text-sm hover:bg-sidebar-accent/50"
                >
                  <span className="truncate">{run.label}</span>
                  <span className="text-xs text-muted-foreground">
                    {run.timestamp}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  )
}
