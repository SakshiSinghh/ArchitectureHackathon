import type { ParsedConstraints, ProjectConstraints, ProjectState } from "@/lib/api-types"

export type OnboardingData = {
  name: string
  location: string
  buildingType: string
  scale: string
  orientation: string
  constraints: {
    lockOrientation: boolean
    lockFacade: boolean
    heightRestriction: boolean
  }
  freeTextConstraints: string
  parsedConstraints: ParsedConstraints
  priorities: {
    daylight: number
    energyEfficiency: number
    cost: number
    aesthetics: number
  }
}

const orientationToDegrees: Record<string, number> = {
  N: 0,
  NE: 45,
  E: 90,
  SE: 135,
  S: 180,
  SW: 225,
  W: 270,
  NW: 315,
}

function scaleDefaults(scale: string) {
  switch (scale) {
    case "low-rise":
      return { floors: 4, height_m: 15, width_m: 24, depth_m: 20 }
    case "mid-rise":
      return { floors: 10, height_m: 36, width_m: 30, depth_m: 24 }
    case "high-rise":
      return { floors: 24, height_m: 90, width_m: 36, depth_m: 30 }
    default:
      return { floors: 6, height_m: 24, width_m: 24, depth_m: 22 }
  }
}

function parseLocation(raw: string): { location_name: string | null; latitude: number | null; longitude: number | null } {
  const parts = raw.split(",").map((part) => part.trim())
  if (parts.length === 2) {
    const lat = Number(parts[0])
    const lon = Number(parts[1])
    if (!Number.isNaN(lat) && !Number.isNaN(lon)) {
      return { location_name: null, latitude: lat, longitude: lon }
    }
  }
  return { location_name: raw || null, latitude: null, longitude: null }
}

function buildStructuredConstraints(data: OnboardingData): string[] {
  const out: string[] = []
  if (data.constraints.lockOrientation) {
    out.push("orientation locked")
  }
  if (data.constraints.lockFacade) {
    out.push("facade intent locked")
  }
  if (data.constraints.heightRestriction) {
    out.push("height capped by zoning")
  }
  return out
}

export function onboardingToProjectState(data: OnboardingData): ProjectState {
  const location = parseLocation(data.location)
  const scale = scaleDefaults(data.scale)

  const constraints: ProjectConstraints = {
    hard_constraints: buildStructuredConstraints(data),
    soft_constraints: [],
    free_text: data.freeTextConstraints || "",
    structured_enabled: true,
    notes: data.freeTextConstraints
      ? "Free-text constraints captured. Use Interpret to propose structured constraints, then accept/edit/reject."
      : null,
  }

  return {
    project_name: data.name || "Untitled Project",
    input_mode: "manual_form",
    brief_text: null,
    site: {
      location_name: location.location_name,
      latitude: location.latitude,
      longitude: location.longitude,
      climate_notes: null,
    },
    building: {
      building_type: data.buildingType || null,
      width_m: scale.width_m,
      depth_m: scale.depth_m,
      height_m: scale.height_m,
      floors: scale.floors,
      orientation_deg: orientationToDegrees[data.orientation] ?? 0,
      window_to_wall_ratio: 0.35,
      geometry_notes: data.scale ? `Initial scale: ${data.scale}` : null,
    },
    constraints,
    priorities: {
      daylight: Number((data.priorities.daylight / 100).toFixed(3)),
      energy: Number((data.priorities.energyEfficiency / 100).toFixed(3)),
      ventilation: 0.2,
      cost: Number((data.priorities.cost / 100).toFixed(3)),
      aesthetics: Number((data.priorities.aesthetics / 100).toFixed(3)),
    },
    provenance: {
      user_provided_fields: [],
      inferred_fields: [],
      defaulted_fields: [],
      unresolved_fields: [],
    },
    assumptions: [],
    validation_issues: [],
    parsed_constraints: data.parsedConstraints,
    climate_context: {},
    baseline_results: {
      summary: "Not computed yet",
      energy_risk: null,
      daylight_potential: null,
      ventilation_potential: null,
      climate_provider: null,
      heat_exposure_score: null,
      solar_exposure_score: null,
      climate_ventilation_score: null,
      narrative_insight: null,
    },
    mitigation_options: [],
  }
}
