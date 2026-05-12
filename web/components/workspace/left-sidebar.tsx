"use client"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { Plus, FolderOpen, Clock, ChevronRight, Plug, X } from "lucide-react"
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
  isOpen?: boolean
  onClose?: () => void
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
  isOpen = false,
  onClose,
}: LeftSidebarProps) {
  const { resetOnboarding } = useOnboarding()

  return (
    <div className={cn(
      "flex h-full w-64 shrink-0 flex-col border-r bg-sidebar",
      // Mobile: fixed overlay drawer, toggled by isOpen
      "fixed inset-y-0 left-0 z-50 transition-transform duration-200 md:relative md:translate-x-0 md:z-auto",
      isOpen ? "translate-x-0" : "-translate-x-full"
    )}>
      {/* Logo + close button */}
      <div className="flex h-16 items-center gap-2 border-b px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <span className="text-sm font-bold text-primary-foreground">A</span>
        </div>
        <div className="flex-1">
          <span className="text-base font-semibold tracking-tight">ArchEnv</span>
          <p className="text-[10px] text-muted-foreground leading-none">Environmental Intelligence</p>
        </div>
        {/* Close button — mobile only */}
        <button
          onClick={onClose}
          className="md:hidden rounded-md p-1 text-muted-foreground hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* New Project Button */}
      <div className="p-4">
        <Button
          className="w-full gap-2"
          variant="outline"
          onClick={() => { resetOnboarding(); onClose?.() }}
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
          className={cn(
            "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors",
            showingGrasshopper
              ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
              : "text-muted-foreground hover:bg-sidebar-accent/50"
          )}
        >
          <Plug className="h-4 w-4 shrink-0" />
          <span className="font-medium">Grasshopper Plugin</span>
        </button>
      </div>
    </div>
  )
}
