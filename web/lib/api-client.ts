import type {
  AgentReviewResponse,
  ConstraintInterpretResponse,
  ProjectDetailResponse,
  ProjectRunsResponse,
  ProjectsListResponse,
  ProjectState,
  RunExecutionResponse,
} from "@/lib/api-types"

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || "http://127.0.0.1:8000"

async function parseOrThrow(response: Response) {
  if (!response.ok) {
    let detail = response.statusText
    try {
      const payload = (await response.json()) as { detail?: string }
      detail = payload.detail || detail
    } catch {
      // Keep default detail when response is not JSON.
    }
    throw new Error(detail)
  }
  return response.json()
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
  })
  return (await parseOrThrow(response)) as T
}

async function post<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  return (await parseOrThrow(response)) as T
}

async function put<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  return (await parseOrThrow(response)) as T
}

export async function getHealth() {
  return get<{ status: string; environment: string; mock_mode: boolean }>("/health")
}

export async function getProjects() {
  return get<ProjectsListResponse>("/api/v1/projects")
}

export async function createProject(payload: {
  project_name: string
  brief_text?: string | null
  notes?: string | null
}) {
  return post<ProjectDetailResponse>("/api/v1/projects", payload)
}

export async function getProject(projectId: string) {
  return get<ProjectDetailResponse>(`/api/v1/projects/${projectId}`)
}

export async function updateProject(projectId: string, projectState: ProjectState, notes?: string | null) {
  return put<ProjectDetailResponse>(`/api/v1/projects/${projectId}`, {
    project_state: projectState,
    notes,
  })
}

export async function getRuns(projectId: string) {
  return get<ProjectRunsResponse>(`/api/v1/projects/${projectId}/runs`)
}

export async function createRun(projectId: string, projectState: ProjectState) {
  return post<RunExecutionResponse>(`/api/v1/projects/${projectId}/runs`, {
    project_state: projectState,
  })
}

export async function runBaseline(projectState: ProjectState) {
  return post<{ project_state: ProjectState }>("/api/v1/analysis/baseline", {
    confirmed: true,
    project_state: projectState,
  })
}

export async function runAgentReview(projectState: ProjectState) {
  return post<AgentReviewResponse>("/api/v1/analysis/agent-review", {
    project_state: projectState,
  })
}

export async function interpretConstraints(projectState: ProjectState, preferredProvider?: string) {
  return post<ConstraintInterpretResponse>("/api/v1/intake/interpret-constraints", {
    project_state: projectState,
    preferred_provider: preferredProvider || null,
  })
}
