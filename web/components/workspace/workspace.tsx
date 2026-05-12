"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import {
  createRun,
  getOrientationOptions,
  getProject,
  getProjects,
  getRuns,
  runAgentReview,
  runBaseline,
  updateProject,
} from "@/lib/api-client"
import type {
  AgentReviewResponse,
  OrientationOptionsResponse,
  ProjectDetailResponse,
  ProjectState,
  RunDiff,
  RunSnapshot,
} from "@/lib/api-types"
import { LeftSidebar } from "./left-sidebar"
import { CenterPanel } from "./center-panel"

type WorkspaceProps = {
  initialProjectId: string | null
}

export function Workspace({ initialProjectId }: WorkspaceProps) {
  const [projectId, setProjectId] = useState<string | null>(initialProjectId)
  const [projects, setProjects] = useState<Array<{ id: string; name: string; updatedAt: string; runCount: number }>>([])
  const [projectDetail, setProjectDetail] = useState<ProjectDetailResponse | null>(null)
  const [draftState, setDraftState] = useState<ProjectState | null>(null)
  const [runs, setRuns] = useState<RunSnapshot[]>([])
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const [latestDiff, setLatestDiff] = useState<RunDiff | null>(null)
  const [baselinePreview, setBaselinePreview] = useState<ProjectState | null>(null)
  const [reviewPreview, setReviewPreview] = useState<AgentReviewResponse | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [orientationOptions, setOrientationOptions] = useState<OrientationOptionsResponse | null>(null)
  const [activeTab, setActiveTab] = useState("project")
  const [error, setError] = useState<string | null>(null)

  const refreshProjects = useCallback(async () => {
    const response = await getProjects()
    const mapped = response.projects.map((project) => ({
      id: project.project_id,
      name: project.project_name,
      updatedAt: project.updated_at,
      runCount: project.run_count,
    }))
    setProjects(mapped)

    if (!projectId && mapped.length > 0) {
      setProjectId(mapped[0].id)
    }
  }, [projectId])

  const loadProject = useCallback(async (id: string) => {
    const [detail, history] = await Promise.all([getProject(id), getRuns(id)])
    setProjectDetail(detail)
    setDraftState(detail.current_state)
    setRuns(history.runs)
    setSelectedRunId(history.runs[0]?.run_id ?? null)
    setLatestDiff(null)
    setBaselinePreview(null)
    setReviewPreview(null)
  }, [])

  useEffect(() => {
    refreshProjects().catch((requestError) => {
      const message = requestError instanceof Error ? requestError.message : "Could not load projects"
      setError(message)
    })
  }, [refreshProjects])

  useEffect(() => {
    if (!projectId) {
      return
    }
    loadProject(projectId).catch((requestError) => {
      const message = requestError instanceof Error ? requestError.message : "Could not load project"
      setError(message)
    })
  }, [projectId, loadProject])

  const selectedRun = useMemo(() => {
    if (!selectedRunId) {
      return null
    }
    return runs.find((run) => run.run_id === selectedRunId) || null
  }, [runs, selectedRunId])

  const handleSave = async () => {
    if (!projectId || !draftState) {
      return
    }
    setError(null)
    setIsSaving(true)
    try {
      const updated = await updateProject(projectId, draftState)
      setProjectDetail(updated)
      setDraftState(updated.current_state)
      await refreshProjects()
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Could not save project"
      setError(message)
    } finally {
      setIsSaving(false)
    }
  }

  const handleRun = async () => {
    if (!projectId || !draftState) {
      return
    }
    setError(null)
    setIsRunning(true)
    try {
      const baseline = await runBaseline(draftState)
      setBaselinePreview(baseline.project_state)

      const review = await runAgentReview(baseline.project_state)
      setReviewPreview(review)

      try {
        const orientOptions = await getOrientationOptions(baseline.project_state)
        setOrientationOptions(orientOptions)
      } catch (_) {
        // orientation options are non-blocking
      }

      const persisted = await createRun(projectId, draftState)
      setLatestDiff(persisted.diff_from_previous)

      const history = await getRuns(projectId)
      setRuns(history.runs)
      setSelectedRunId(persisted.run.run_id)

      const latestProject = await getProject(projectId)
      setProjectDetail(latestProject)
      setDraftState(latestProject.current_state)
      await refreshProjects()
      setActiveTab("insights")
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Could not run analysis"
      setError(message)
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <LeftSidebar
        projects={projects}
        activeProjectId={projectId}
        onSelectProject={(id) => { setProjectId(id); setActiveTab("project") }}
        runs={runs}
        selectedRunId={selectedRunId}
        onSelectRun={setSelectedRunId}
        onGrasshopperClick={() => setActiveTab((t) => t === "grasshopper" ? "project" : "grasshopper")}
        showingGrasshopper={activeTab === "grasshopper"}
      />
      <div className="flex-1 overflow-hidden">
        <CenterPanel
          projectId={projectId}
          state={draftState}
          onStateChange={setDraftState}
          onSave={handleSave}
          onRun={handleRun}
          isSaving={isSaving}
          isRunning={isRunning}
          error={error}
          review={reviewPreview || selectedRun?.agent_review || null}
          diff={latestDiff}
          run={selectedRun}
          orientationOptions={orientationOptions}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
      </div>
    </div>
  )
}
