"""Streamlit project workspace for iterative design negotiation cycles."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from shared.project_state import ProjectState


DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def _init_session_state() -> None:
    defaults = {
        "backend_url": DEFAULT_BACKEND_URL,
        "projects": [],
        "selected_project_id": None,
        "project_detail": None,
        "runs": [],
        "latest_run_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _get(path: str) -> dict[str, Any] | None:
    try:
        response = requests.get(f"{st.session_state.backend_url.rstrip('/')}{path}", timeout=30)
    except requests.RequestException as error:
        st.error(f"Could not call {path}: {error}")
        return None

    if response.status_code >= 400:
        detail = _read_detail(response)
        st.error(f"Request failed for {path}: {detail}")
        return None
    return response.json()


def _post(path: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    try:
        response = requests.post(
            f"{st.session_state.backend_url.rstrip('/')}{path}",
            json=payload,
            timeout=45,
        )
    except requests.RequestException as error:
        st.error(f"Could not call {path}: {error}")
        return None

    if response.status_code >= 400:
        detail = _read_detail(response)
        st.error(f"Request failed for {path}: {detail}")
        return None
    return response.json()


def _put(path: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    try:
        response = requests.put(
            f"{st.session_state.backend_url.rstrip('/')}{path}",
            json=payload,
            timeout=45,
        )
    except requests.RequestException as error:
        st.error(f"Could not call {path}: {error}")
        return None

    if response.status_code >= 400:
        detail = _read_detail(response)
        st.error(f"Request failed for {path}: {detail}")
        return None
    return response.json()


def _read_detail(response: requests.Response) -> str:
    try:
        return str(response.json().get("detail", response.text))
    except Exception:
        return response.text


def _refresh_projects() -> None:
    payload = _get("/api/v1/projects")
    if payload is None:
        return
    st.session_state.projects = payload.get("projects", [])


def _load_project(project_id: str) -> None:
    detail = _get(f"/api/v1/projects/{project_id}")
    runs = _get(f"/api/v1/projects/{project_id}/runs")
    if detail is None or runs is None:
        return

    st.session_state.project_detail = detail
    st.session_state.runs = runs.get("runs", [])


def _project_state() -> dict[str, Any] | None:
    detail = st.session_state.project_detail
    if not detail:
        return None
    return detail.get("current_state")


def _constraints_as_text(values: list[str]) -> str:
    return "\n".join(values or [])


def _parse_constraints(raw_text: str) -> list[str]:
    normalized = raw_text.replace(",", "\n")
    return [line.strip() for line in normalized.splitlines() if line.strip()]


def _build_state_from_form(current: dict[str, Any]) -> dict[str, Any]:
    site = current.get("site", {})
    building = current.get("building", {})
    priorities = current.get("priorities", {})
    constraints = current.get("constraints", {})

    intent_col, site_col = st.columns(2)
    with intent_col:
        project_name = st.text_input("Project name", value=current.get("project_name", "Untitled Project"))
        brief_text = st.text_area(
            "Design intent",
            value=current.get("brief_text") or "",
            placeholder="What are you trying to achieve in this iteration?",
        )
        building_type = st.selectbox(
            "Building type",
            ["office", "residential", "mixed_use", "hospitality", "institutional", "industrial", "other"],
            index=_safe_index(["office", "residential", "mixed_use", "hospitality", "institutional", "industrial", "other"], building.get("building_type") or "office"),
        )
        geometry_notes = st.text_area(
            "Geometry notes",
            value=building.get("geometry_notes") or "",
            placeholder="Key massing intentions, adjacencies, daylight concerns...",
        )

    with site_col:
        location_name = st.text_input("Location name", value=site.get("location_name") or "")
        latitude = st.number_input("Latitude (optional)", value=float(site.get("latitude") or 0.0), format="%.6f")
        longitude = st.number_input("Longitude (optional)", value=float(site.get("longitude") or 0.0), format="%.6f")
        climate_notes = st.text_area("Climate notes", value=site.get("climate_notes") or "")

    st.markdown("### Constraints and priorities")
    c1, c2 = st.columns(2)
    with c1:
        hard_constraints = st.text_area(
            "Hard constraints",
            value=_constraints_as_text(constraints.get("hard_constraints", [])),
            help="One per line or comma-separated.",
        )
        soft_constraints = st.text_area(
            "Soft constraints",
            value=_constraints_as_text(constraints.get("soft_constraints", [])),
            help="One per line or comma-separated.",
        )

    with c2:
        floors = st.slider("Floors", min_value=1, max_value=80, value=int(building.get("floors") or 6))
        height_m = st.number_input("Approx height (m)", min_value=1.0, value=float(building.get("height_m") or 24.0))
        orientation_deg = st.slider(
            "Orientation (degrees)",
            min_value=0,
            max_value=359,
            value=int(building.get("orientation_deg") or 90),
        )
        window_to_wall_ratio = st.slider(
            "Glazing intent (window-to-wall ratio)",
            min_value=0.0,
            max_value=1.0,
            value=float(building.get("window_to_wall_ratio") or 0.35),
            step=0.01,
        )
        width_m = st.number_input("Approx width (m)", min_value=1.0, value=float(building.get("width_m") or 20.0))
        depth_m = st.number_input("Approx depth (m)", min_value=1.0, value=float(building.get("depth_m") or 30.0))

    p1, p2, p3, p4, p5 = st.columns(5)
    energy = p1.slider("Energy", 0.0, 1.0, float(priorities.get("energy") or 0.25), 0.01)
    daylight = p2.slider("Daylight", 0.0, 1.0, float(priorities.get("daylight") or 0.2), 0.01)
    ventilation = p3.slider("Ventilation", 0.0, 1.0, float(priorities.get("ventilation") or 0.2), 0.01)
    cost = p4.slider("Cost", 0.0, 1.0, float(priorities.get("cost") or 0.2), 0.01)
    aesthetics = p5.slider("Aesthetics", 0.0, 1.0, float(priorities.get("aesthetics") or 0.15), 0.01)

    current["project_name"] = project_name
    current["brief_text"] = brief_text.strip() or None
    current.setdefault("site", {})
    current["site"].update(
        {
            "location_name": location_name.strip() or None,
            "latitude": latitude if latitude != 0.0 else None,
            "longitude": longitude if longitude != 0.0 else None,
            "climate_notes": climate_notes.strip() or None,
        }
    )

    current.setdefault("building", {})
    current["building"].update(
        {
            "building_type": building_type,
            "width_m": width_m,
            "depth_m": depth_m,
            "height_m": height_m,
            "floors": floors,
            "orientation_deg": float(orientation_deg),
            "window_to_wall_ratio": window_to_wall_ratio,
            "geometry_notes": geometry_notes.strip() or None,
        }
    )

    current.setdefault("constraints", {})
    current["constraints"]["hard_constraints"] = _parse_constraints(hard_constraints)
    current["constraints"]["soft_constraints"] = _parse_constraints(soft_constraints)

    current.setdefault("priorities", {})
    current["priorities"].update(
        {
            "energy": energy,
            "daylight": daylight,
            "ventilation": ventilation,
            "cost": cost,
            "aesthetics": aesthetics,
        }
    )

    return current


def _safe_index(options: list[str], value: str) -> int:
    try:
        return options.index(value)
    except ValueError:
        return 0


def _render_run_results(run_payload: dict[str, Any]) -> None:
    baseline_state = run_payload.get("baseline_state", {})
    baseline = baseline_state.get("baseline_results", {})
    climate_context = baseline_state.get("climate_context", {})
    climate_metrics = climate_context.get("environmental_metrics", {})
    review = run_payload.get("agent_review", {})

    st.markdown("## Results and recommendations")
    m1, m2, m3 = st.columns(3)
    m1.metric("Energy risk", baseline.get("energy_risk", "n/a"))
    m2.metric("Daylight potential", baseline.get("daylight_potential", "n/a"))
    m3.metric("Ventilation potential", baseline.get("ventilation_potential", "n/a"))

    c1, c2, c3 = st.columns(3)
    c1.metric("Climate provider", run_payload.get("climate_provider") or climate_context.get("provider", "n/a"))
    c2.metric("Source tier", run_payload.get("climate_source_tier") or climate_context.get("source_tier", "n/a"))
    c3.metric("Location", climate_context.get("location", "n/a"))

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Avg temp", climate_metrics.get("avg_temp", "n/a"))
    s2.metric("Peak temp", climate_metrics.get("peak_temp", "n/a"))
    s3.metric("Avg wind", climate_metrics.get("avg_wind_speed", "n/a"))
    s4.metric("Avg solar", climate_metrics.get("avg_solar_radiation", "n/a"))

    e1, e2, e3 = st.columns(3)
    e1.metric("Heat exposure", climate_metrics.get("heat_exposure_score", "n/a"))
    e2.metric("Solar exposure", climate_metrics.get("solar_exposure_score", "n/a"))
    e3.metric("Ventilation potential score", climate_metrics.get("ventilation_potential_score", "n/a"))

    st.markdown("### Agent recommendations")
    st.info(review.get("top_option_reason", "No top option reason available."))
    st.warning(review.get("penalty_summary", "No penalty summary available."))

    for option in review.get("ranked_options", []):
        st.markdown(f"{option.get('rank', '-')}. {option.get('title', 'Untitled')} (score={option.get('score', 0)})")
        st.write(option.get("description", ""))
        st.caption(f"Rationale: {option.get('rationale', '')}")


def _render_what_changed(diff_payload: dict[str, Any] | None) -> None:
    st.markdown("## What changed")
    if not diff_payload:
        st.info("No previous run available yet. Run another cycle to see comparisons.")
        return

    changed_inputs = diff_payload.get("changed_inputs") or []
    changed_baseline_metrics = diff_payload.get("changed_baseline_metrics") or {}
    changed_top = diff_payload.get("changed_top_recommendation") or {}
    changed_deltas = diff_payload.get("changed_agent_deltas") or {}

    st.markdown("### Changed inputs")
    if changed_inputs:
        st.write(changed_inputs)
    else:
        st.write("No input differences from previous run.")

    st.markdown("### Baseline metric changes")
    if changed_baseline_metrics:
        st.json(changed_baseline_metrics)
    else:
        st.write("No baseline metric changes.")

    st.markdown("### Top recommendation change")
    if changed_top:
        st.json(changed_top)
    else:
        st.write("Top recommendation unchanged.")

    st.markdown("### Agent delta changes")
    if changed_deltas:
        st.json(changed_deltas)
    else:
        st.write("No constrained-vs-baseline delta changes.")


_init_session_state()

st.set_page_config(page_title="Design Negotiation Workspace", layout="wide")
st.title("Design Negotiation Workspace")
st.caption("Project-based workflow with saved states, iterative runs, and change visibility.")

with st.sidebar:
    st.header("Projects")
    st.session_state.backend_url = st.text_input("Backend URL", value=st.session_state.backend_url).rstrip("/")

    col_refresh, col_health = st.columns(2)
    if col_refresh.button("Refresh projects"):
        _refresh_projects()

    if col_health.button("Check API"):
        health = _get("/health")
        if health:
            st.success(f"API ok | env={health.get('environment')} | mock={health.get('mock_mode')}")

    if not st.session_state.projects:
        _refresh_projects()

    project_options = [project["project_id"] for project in st.session_state.projects]
    project_labels = {
        project["project_id"]: f"{project['project_name']} ({project['run_count']} runs)"
        for project in st.session_state.projects
    }

    selected = st.selectbox(
        "Select project",
        options=project_options,
        format_func=lambda pid: project_labels.get(pid, pid),
        index=project_options.index(st.session_state.selected_project_id)
        if st.session_state.selected_project_id in project_options
        else 0,
    ) if project_options else None

    if selected and selected != st.session_state.selected_project_id:
        st.session_state.selected_project_id = selected
        _load_project(selected)

    st.markdown("---")
    st.subheader("Create project")
    with st.form("create_project_form"):
        new_project_name = st.text_input("Project name", value="")
        new_project_brief = st.text_area("Initial design intent", value="")
        new_project_notes = st.text_area("Workspace notes", value="")
        create_submitted = st.form_submit_button("Create project")

    if create_submitted:
        if not new_project_name.strip():
            st.error("Project name is required.")
        else:
            created = _post(
                "/api/v1/projects",
                {
                    "project_name": new_project_name.strip(),
                    "brief_text": new_project_brief.strip() or None,
                    "notes": new_project_notes.strip() or None,
                },
            )
            if created:
                _refresh_projects()
                st.session_state.selected_project_id = created["project"]["project_id"]
                st.session_state.project_detail = created
                st.session_state.runs = []
                st.session_state.latest_run_result = None
                st.success("Project created.")

    if st.session_state.selected_project_id:
        st.markdown("---")
        st.subheader("Run history")
        if st.session_state.runs:
            run_ids = [run["run_id"] for run in st.session_state.runs]
            selected_run_id = st.selectbox("Saved runs", run_ids)
            selected_run = next((run for run in st.session_state.runs if run["run_id"] == selected_run_id), None)
            if selected_run is not None:
                st.caption(f"Top rec: {selected_run.get('top_recommendation') or 'n/a'}")
                if st.button("Show selected run"):
                    st.session_state.latest_run_result = {
                        "run": selected_run,
                        "diff_from_previous": None,
                    }
        else:
            st.caption("No runs yet for this project.")

project_detail = st.session_state.project_detail
if not project_detail:
    st.info("Create or select a project from the sidebar to start an iterative design workflow.")
    st.stop()

current_state = _project_state()
if current_state is None:
    st.error("Current project state could not be loaded.")
    st.stop()

st.markdown("## 1. Design intent")
edited_state = _build_state_from_form(json.loads(json.dumps(current_state)))

st.markdown("## 2. Confirm current state")
confirm_ready = st.checkbox("I confirm this state is ready to save and evaluate.", value=False)

save_col, run_col = st.columns(2)
if save_col.button("Save current state"):
    try:
        validated = ProjectState.model_validate(edited_state)
    except Exception as error:
        st.error(f"State is invalid and was not saved: {error}")
    else:
        updated = _put(
            f"/api/v1/projects/{project_detail['project']['project_id']}",
            {"project_state": validated.model_dump(mode="json")},
        )
        if updated:
            st.session_state.project_detail = updated
            st.success("Current state saved.")

if run_col.button("Run baseline + agent review cycle", disabled=not confirm_ready):
    try:
        validated = ProjectState.model_validate(edited_state)
    except Exception as error:
        st.error(f"State is invalid and cannot be evaluated: {error}")
    else:
        run_response = _post(
            f"/api/v1/projects/{project_detail['project']['project_id']}/runs",
            {"project_state": validated.model_dump(mode="json")},
        )
        if run_response:
            st.session_state.latest_run_result = run_response
            _load_project(project_detail["project"]["project_id"])
            st.success("Design negotiation cycle completed and saved to run history.")

if st.expander("Advanced: edit full state JSON"):
    raw_json = st.text_area("Project state JSON", value=json.dumps(edited_state, indent=2), height=260)
    if st.button("Apply JSON override"):
        try:
            parsed = json.loads(raw_json)
            validated = ProjectState.model_validate(parsed)
            updated = _put(
                f"/api/v1/projects/{project_detail['project']['project_id']}",
                {"project_state": validated.model_dump(mode="json")},
            )
            if updated:
                st.session_state.project_detail = updated
                st.success("JSON override applied.")
        except Exception as error:
            st.error(f"Invalid JSON state: {error}")

latest_run = st.session_state.latest_run_result
if latest_run:
    _render_run_results(latest_run.get("run", {}))
    _render_what_changed(latest_run.get("diff_from_previous"))
else:
    st.info("No run executed in this session yet. Use the run cycle button to create an iteration snapshot.")
