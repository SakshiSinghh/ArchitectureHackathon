"use client"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { Plus, FolderOpen, Clock, ChevronRight, Plug } from "lucide-react"
import { useOnboarding } from "@/lib/onboarding-context"
import type { RunSnapshot } from "@/lib/api-types"

type ProjectItem = {
  id: string
  name: string
  updatedAt: string
  runCount: number
}

type LeftSidebarProps = {
  projects: ProjectItem[]
  activeProjectId: string | null
  onSelectProject: (projectId: string) => void
  runs: RunSnapshot[]
  selectedRunId: string | null
  onSelectRun: (runId: string) => void
  onGrasshopperClick: () => void
  showingGrasshopper: boolean
}

export function LeftSidebar({
  projects,
  activeProjectId,
  onSelectProject,
  runs,
  selectedRunId,
  onSelectRun,
  onGrasshopperClick,
  showingGrasshopper,
}: LeftSidebarProps) {
  const { resetOnboarding } = useOnboarding()

  return (
    <div className="flex h-full w-64 flex-col border-r bg-sidebar">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <span className="text-sm font-bold text-primary-foreground">A</span>
        </div>
        <div>
          <span className="text-base font-semibold tracking-tight">ArchEnv</span>
          <p className="text-[10px] text-muted-foreground leading-none">Environmental Intelligence</p>
        </div>
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
                  onClick={() => onSelectProject(project.id)}
                  className={cn(
                    "flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition-colors",
                    activeProjectId === project.id
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "hover:bg-sidebar-accent/50"
                  )}
                >
                  <div className="min-w-0 flex-1">
                    <div className="truncate font-medium">{project.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(project.updatedAt).toLocaleString()} · {project.runCount} runs
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
              {runs.length === 0 ? <p className="px-3 py-2 text-xs text-muted-foreground">No runs yet</p> : null}
              {runs.map((run) => (
                <button
                  key={run.run_id}
                  onClick={() => onSelectRun(run.run_id)}
                  className={cn(
                    "flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors hover:bg-sidebar-accent/50",
                    selectedRunId === run.run_id ? "bg-sidebar-accent text-sidebar-accent-foreground" : ""
                  )}
                >
                  <span className="truncate">{run.top_recommendation || "Run snapshot"}</span>
                  <span className="text-xs text-muted-foreground">{new Date(run.created_at).toLocaleTimeString()}</span>
                </button>
              ))}
            </div>
          </div>
        </ScrollArea>
      </div>

      {/* Grasshopper Plugin */}
      <div className="border-t p-3">
        <button
          onClick={onGrasshopperClick}
          className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
            showingGrasshopper
              ? "bg-green-600 text-white"
              : "hover:bg-sidebar-accent/50 text-muted-foreground"
          }`}
        >
          <Plug className="h-4 w-4 shrink-0" />
          <span className="font-medium">Grasshopper Plugin</span>
        </button>
      </div>
    </div>
  )
}
