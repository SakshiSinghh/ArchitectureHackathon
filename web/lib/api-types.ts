export type Site = {
  location_name: string | null
  latitude: number | null
  longitude: number | null
  climate_notes: string | null
}

export type Building = {
  building_type: string | null
  width_m: number | null
  depth_m: number | null
  height_m: number | null
  floors: number | null
  orientation_deg: number | null
  window_to_wall_ratio: number | null
  geometry_notes: string | null
}

export type Priorities = {
  energy: number
  daylight: number
  ventilation: number
  cost: number
  aesthetics: number
}

export type ProjectConstraints = {
  hard_constraints: string[]
  soft_constraints: string[]
  free_text: string
  structured_enabled: boolean
  notes: string | null
  parsed_hard_constraints?: string[]
  effective_hard_constraints?: string[]
}

export type ParsedConstraintStatus = "proposed" | "accepted" | "rejected" | "edited"

export type ParsedConstraintItem = {
  source_text: string
  normalized_key: string
  normalized_value: string | number | boolean | null
  confidence: number
  rationale: string
  status: ParsedConstraintStatus
}

export type ParsedConstraints = {
  extracted_items: ParsedConstraintItem[]
  unresolved_items: string[]
  confidence_label: "low" | "medium" | "high"
  confidence_score: number
  parser_provider: string
  parser_mode: "llm" | "heuristic" | "fallback" | "none"
  notes: string[]
  conflict_warnings: string[]
}

export type BaselineResults = {
  summary: string
  energy_risk: number | null
  daylight_potential: number | null
  ventilation_potential: number | null
  climate_provider: string | null
  heat_exposure_score: number | null
  solar_exposure_score: number | null
  climate_ventilation_score: number | null
  narrative_insight: string | null
}

export type ProjectState = {
  project_name: string
  input_mode: "manual_form" | "pasted_brief" | "uploaded_json"
  brief_text: string | null
  site: Site
  building: Building
  constraints: ProjectConstraints
  priorities: Priorities
  provenance: {
    user_provided_fields: string[]
    inferred_fields: string[]
    defaulted_fields: string[]
    unresolved_fields: string[]
  }
  assumptions: string[]
  validation_issues: Array<{ severity: "info" | "warning" | "error"; field: string; message: string }>
  parsed_constraints: ParsedConstraints
  climate_context: Record<string, unknown>
  baseline_results: BaselineResults
  mitigation_options: Array<{
    title: string
    description: string
    expected_benefit: string
    tradeoff_note: string
  }>
}

export type ConstraintInterpretResponse = {
  parsed_constraints: ParsedConstraints
}

export type RankedMitigation = {
  rank: number
  title: string
  description: string
  rationale: string
  expected_benefit: string
  tradeoff_note: string
  score: number
}

export type AgentReviewResponse = {
  baseline_metrics: {
    energy_risk: number
    daylight_potential: number
    ventilation_potential: number
  }
  constrained_metrics: {
    energy_risk: number
    daylight_potential: number
    ventilation_potential: number
  }
  metric_deltas: {
    energy_risk_delta: number
    daylight_potential_delta: number
    ventilation_potential_delta: number
  }
  penalty_summary: string
  ranked_options: RankedMitigation[]
  top_option_reason: string
}

export type ProjectMeta = {
  project_id: string
  project_name: string
  created_at: string
  updated_at: string
  notes: string | null
}

export type ProjectSummary = {
  project_id: string
  project_name: string
  created_at: string
  updated_at: string
  run_count: number
}

export type RunSnapshot = {
  run_id: string
  created_at: string
  input_state: ProjectState
  baseline_state: ProjectState
  agent_review: AgentReviewResponse
  top_recommendation: string | null
  climate_provider: string | null
  climate_source_tier: string | null
}

export type RunDiff = {
  changed_inputs: string[]
  changed_baseline_metrics: Record<string, { previous: number | string | null; current: number | string | null }>
  changed_top_recommendation: { previous?: string | null; current?: string | null }
  changed_agent_deltas: Record<string, { previous: number | null; current: number | null }>
}

export type ProjectDetailResponse = {
  project: ProjectMeta
  current_state: ProjectState
  recent_run_ids: string[]
}

export type ProjectsListResponse = {
  projects: ProjectSummary[]
}

export type ProjectRunsResponse = {
  project_id: string
  runs: RunSnapshot[]
}

export type RunExecutionResponse = {
  run: RunSnapshot
  diff_from_previous: RunDiff | null
}

export type RoomAnalysis = {
  room_name: string
  facade_orientations: string[]
  is_external: boolean
  environmental_issues: string[]
  suggestions: string[]
}

export type FloorPlanAnalysis = {
  primary_orientation_deg: number | null
  north_assumption: string
  rooms: RoomAnalysis[]
  overall_issues: string[]
  overall_suggestions: string[]
  confidence: "low" | "medium" | "high"
  analysis_notes: string | null
  provider: string
}

export type FloorPlanUploadResponse = {
  project_id: string
  floor_plan_analysis: FloorPlanAnalysis
  updated_building: Building
}

export type OrientationOption = {
  orientation_deg: number
  label: string
  rank: number
  energy_risk: number
  daylight_potential: number
  ventilation_potential: number
  composite_score: number
  narrative: string
  is_current: boolean
}

export type OrientationOptionsResponse = {
  options: OrientationOption[]
  recommended_orientation_deg: number
  location: string | null
}
