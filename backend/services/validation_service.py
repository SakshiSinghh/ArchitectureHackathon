"""Validation checks for completeness and contradictions in project state."""

from __future__ import annotations

import re

from shared.project_state import ProjectState, ValidationIssue


REQUIRED_FIELDS = [
    "site.location_name",
    "building.building_type",
    "building.width_m",
    "building.depth_m",
    "building.height_m",
    "building.orientation_deg",
]


def validate_project_state(project: ProjectState) -> list[ValidationIssue]:
    """Return warnings/errors for missing or conflicting values."""

    issues: list[ValidationIssue] = []

    if not project.site.location_name:
        issues.append(
            ValidationIssue(
                severity="error",
                field="site.location_name",
                message="Site location is required for climate context.",
            )
        )

    if project.site.location_name and (project.site.latitude is None or project.site.longitude is None):
        issues.append(
            ValidationIssue(
                severity="warning",
                field="site.coordinates",
                message="Latitude/longitude missing; location-based context is less reliable.",
            )
        )

    if project.site.latitude is not None and not -90 <= project.site.latitude <= 90:
        issues.append(
            ValidationIssue(
                severity="error",
                field="site.latitude",
                message="Latitude must be between -90 and 90.",
            )
        )

    if project.site.longitude is not None and not -180 <= project.site.longitude <= 180:
        issues.append(
            ValidationIssue(
                severity="error",
                field="site.longitude",
                message="Longitude must be between -180 and 180.",
            )
        )

    if not project.building.building_type:
        issues.append(
            ValidationIssue(
                severity="warning",
                field="building.building_type",
                message="Building type is missing; assumptions will be less reliable.",
            )
        )

    for dimension_field in ["width_m", "depth_m", "height_m"]:
        value = getattr(project.building, dimension_field)
        if value is not None and value <= 0:
            issues.append(
                ValidationIssue(
                    severity="error",
                    field=f"building.{dimension_field}",
                    message="Dimension values must be greater than zero.",
                )
            )

    if project.building.width_m is not None and project.building.width_m > 300:
        issues.append(
            ValidationIssue(
                severity="warning",
                field="building.width_m",
                message="Width is unusually large for early-stage massing; verify units.",
            )
        )

    if project.building.depth_m is not None and project.building.depth_m > 300:
        issues.append(
            ValidationIssue(
                severity="warning",
                field="building.depth_m",
                message="Depth is unusually large for early-stage massing; verify units.",
            )
        )

    if project.building.height_m is not None and project.building.height_m > 500:
        issues.append(
            ValidationIssue(
                severity="warning",
                field="building.height_m",
                message="Height is unusually large; verify scale and floors.",
            )
        )

    if project.building.orientation_deg is not None and not 0 <= project.building.orientation_deg <= 359:
        issues.append(
            ValidationIssue(
                severity="error",
                field="building.orientation_deg",
                message="Orientation must be between 0 and 359 degrees.",
            )
        )

    if (
        project.building.window_to_wall_ratio is not None
        and not 0 <= project.building.window_to_wall_ratio <= 1
    ):
        issues.append(
            ValidationIssue(
                severity="error",
                field="building.window_to_wall_ratio",
                message="Window-to-wall ratio should be in [0, 1].",
            )
        )

    if project.provenance.unresolved_fields:
        issues.append(
            ValidationIssue(
                severity="warning",
                field="provenance.unresolved_fields",
                message="Some required fields are unresolved and need user confirmation.",
            )
        )

    if (
        project.building.floors is not None
        and project.building.height_m is not None
        and project.building.floors > 0
        and project.building.height_m / project.building.floors < 2.4
    ):
        issues.append(
            ValidationIssue(
                severity="warning",
                field="building.floors",
                message="Height per floor is unusually low; check geometry values.",
            )
        )

    if (
        project.building.floors is not None
        and project.building.height_m is not None
        and project.building.floors > 0
        and project.building.height_m / project.building.floors > 6.0
    ):
        issues.append(
            ValidationIssue(
                severity="warning",
                field="building.floors",
                message="Height per floor is unusually high; check geometry and floor count.",
            )
        )

    priorities = [
        project.priorities.energy,
        project.priorities.daylight,
        project.priorities.ventilation,
        project.priorities.cost,
        project.priorities.aesthetics,
    ]
    if any(priority < 0 for priority in priorities):
        issues.append(
            ValidationIssue(
                severity="error",
                field="priorities",
                message="Priority weights cannot be negative.",
            )
        )

    if all(abs(priority - priorities[0]) < 1e-9 for priority in priorities):
        issues.append(
            ValidationIssue(
                severity="info",
                field="priorities",
                message="All priorities are equal; trade-off ranking may be less informative.",
            )
        )

    if sum(priorities) <= 0:
        issues.append(
            ValidationIssue(
                severity="warning",
                field="priorities",
                message="Total priority weight is non-positive; defaults may be used.",
            )
        )

    for constraint in project.constraints.get("hard_constraints", []):
        normalized = constraint.lower()
        if "max height" in normalized and project.building.height_m is not None:
            max_height_match = re.search(r"(\d+(?:\.\d+)?)", normalized)
            if max_height_match:
                limit = float(max_height_match.group(1))
                if project.building.height_m > limit:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            field="constraints.hard_constraints",
                            message=(
                                f"Building height ({project.building.height_m}m) exceeds hard constraint max height ({limit}m)."
                            ),
                        )
                    )

        if "orientation" in normalized and project.building.orientation_deg is not None:
            locked_orientation = re.search(r"(\d+(?:\.\d+)?)", normalized)
            if locked_orientation:
                target = float(locked_orientation.group(1))
                if abs(project.building.orientation_deg - target) > 15:
                    issues.append(
                        ValidationIssue(
                            severity="info",
                            field="constraints.hard_constraints",
                            message=(
                                f"Orientation ({project.building.orientation_deg}°) may conflict with locked orientation ({target}°)."
                            ),
                        )
                    )

    return issues
