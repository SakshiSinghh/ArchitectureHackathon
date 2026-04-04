"""Streamlit frontend for Phase 2 intake, baseline, and agent review workflow."""

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
        "intake_response": None,
        "normalized_state": None,
        "baseline_response": None,
        "agent_review_response": None,
        "confirmed": False,
        "editable_state_json": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _manual_payload_form() -> dict[str, Any]:
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Project name", value="Untitled Project")
        location_name = st.text_input("Location name")
        latitude = st.number_input("Latitude", value=0.0, format="%.6f")
        longitude = st.number_input("Longitude", value=0.0, format="%.6f")
        building_type = st.text_input("Building type", value="office")
        width_m = st.number_input("Width (m)", min_value=0.0, value=20.0)
        depth_m = st.number_input("Depth (m)", min_value=0.0, value=30.0)

    with col2:
        height_m = st.number_input("Height (m)", min_value=0.0, value=24.0)
        floors = st.number_input("Floors", min_value=1, value=6)
        orientation_deg = st.number_input("Orientation (deg)", min_value=0.0, max_value=359.0, value=90.0)
        window_to_wall_ratio = st.slider("Window-to-wall ratio", min_value=0.0, max_value=1.0, value=0.35)
        hard_constraints = st.text_area(
            "Hard constraints (comma-separated)",
            placeholder="e.g., max height 30m, orientation 90",
        )
        soft_constraints = st.text_area(
            "Soft constraints (comma-separated)",
            placeholder="e.g., maximize views, maintain facade rhythm",
        )

    st.subheader("Priorities")
    pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns(5)
    energy = pcol1.slider("Energy", min_value=0.0, max_value=1.0, value=0.25)
    daylight = pcol2.slider("Daylight", min_value=0.0, max_value=1.0, value=0.2)
    ventilation = pcol3.slider("Ventilation", min_value=0.0, max_value=1.0, value=0.2)
    cost = pcol4.slider("Cost", min_value=0.0, max_value=1.0, value=0.2)
    aesthetics = pcol5.slider("Aesthetics", min_value=0.0, max_value=1.0, value=0.15)

    return {
        "project_name": project_name,
        "location_name": location_name.strip() or None,
        "latitude": latitude if latitude != 0.0 else None,
        "longitude": longitude if longitude != 0.0 else None,
        "building_type": building_type.strip() or None,
        "width_m": width_m,
        "depth_m": depth_m,
        "height_m": height_m,
        "floors": floors,
        "orientation_deg": orientation_deg,
        "window_to_wall_ratio": window_to_wall_ratio,
        "hard_constraints": hard_constraints,
        "soft_constraints": soft_constraints,
        "priority_energy": energy,
        "priority_daylight": daylight,
        "priority_ventilation": ventilation,
        "priority_cost": cost,
        "priority_aesthetics": aesthetics,
    }


def _build_raw_payload(input_mode: str) -> dict[str, Any] | str:
    if input_mode == "manual_form":
        st.subheader("Step B: Manual project input")
        return _manual_payload_form()

    if input_mode == "pasted_brief":
        st.subheader("Step B: Paste design brief")
        st.info(
            "Brief parsing is heuristic. Use key:value lines for best extraction (example: location: Pune)."
        )
        return st.text_area("Brief text", height=220, placeholder="Paste your brief here...")

    st.subheader("Step B: Upload JSON")
    st.caption("Expected shape: canonical ProjectState object with site/building/constraints/priorities keys.")
    uploaded = st.file_uploader("Upload JSON file", type=["json"])
    if uploaded is None:
        return {}
    try:
        return json.load(uploaded)
    except json.JSONDecodeError as error:
        st.error(f"Invalid JSON file: {error}")
        return {}


def _post(backend_url: str, path: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    try:
        response = requests.post(f"{backend_url}{path}", json=payload, timeout=30)
    except requests.RequestException as error:
        st.error(f"Could not connect to backend endpoint {path}: {error}")
        return None

    if response.status_code >= 400:
        detail = response.json().get("detail", response.text)
        st.error(f"Request to {path} failed: {detail}")
        return None
    return response.json()


def _render_validation_issues(issues: list[dict[str, Any]]) -> None:
    st.subheader("Validation issues")
    if not issues:
        st.success("No validation issues detected in current normalized state.")
        return

    for issue in issues:
        severity = issue.get("severity")
        message = f"{issue.get('field')}: {issue.get('message')}"
        if severity == "error":
            st.error(message)
        elif severity == "warning":
            st.warning(message)
        else:
            st.info(message)


def _render_provenance(provenance: dict[str, Any]) -> None:
    st.subheader("Provenance")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**User-provided fields**")
        st.write(provenance.get("user_provided_fields", []) or ["None"])
        st.markdown("**Inferred fields**")
        st.write(provenance.get("inferred_fields", []) or ["None"])
    with c2:
        st.markdown("**Defaulted fields**")
        st.write(provenance.get("defaulted_fields", []) or ["None"])
        st.markdown("**Unresolved fields**")
        st.write(provenance.get("unresolved_fields", []) or ["None"])


def _render_baseline(result_state: dict[str, Any]) -> None:
    baseline = result_state.get("baseline_results", {})
    st.subheader("Step F: Baseline results")
    m1, m2, m3 = st.columns(3)
    m1.metric("Energy risk", baseline.get("energy_risk", "n/a"))
    m2.metric("Daylight potential", baseline.get("daylight_potential", "n/a"))
    m3.metric("Ventilation potential", baseline.get("ventilation_potential", "n/a"))

    if baseline.get("summary"):
        st.markdown("**Summary**")
        st.write(baseline["summary"])

    if baseline.get("narrative_insight"):
        st.markdown("**Narrative insight**")
        st.info(baseline["narrative_insight"])

    st.markdown("**Climate/context summary**")
    st.json(result_state.get("climate_context", {}))


def _render_agent_review(agent_review: dict[str, Any]) -> None:
    st.subheader("Step H: Ranked mitigation options and deltas")

    c1, c2, c3 = st.columns(3)
    baseline_metrics = agent_review.get("baseline_metrics", {})
    constrained_metrics = agent_review.get("constrained_metrics", {})
    deltas = agent_review.get("metric_deltas", {})

    c1.metric(
        "Energy risk Δ",
        f"{deltas.get('energy_risk_delta', 0):+.3f}",
        delta=f"Base {baseline_metrics.get('energy_risk', 'n/a')} → Constrained {constrained_metrics.get('energy_risk', 'n/a')}",
    )
    c2.metric(
        "Daylight potential Δ",
        f"{deltas.get('daylight_potential_delta', 0):+.3f}",
        delta=(
            f"Base {baseline_metrics.get('daylight_potential', 'n/a')} → "
            f"Constrained {constrained_metrics.get('daylight_potential', 'n/a')}"
        ),
    )
    c3.metric(
        "Ventilation potential Δ",
        f"{deltas.get('ventilation_potential_delta', 0):+.3f}",
        delta=(
            f"Base {baseline_metrics.get('ventilation_potential', 'n/a')} → "
            f"Constrained {constrained_metrics.get('ventilation_potential', 'n/a')}"
        ),
    )

    st.markdown("**Penalty summary**")
    st.warning(agent_review.get("penalty_summary", "No penalty summary."))

    st.markdown("**Top option rationale**")
    st.info(agent_review.get("top_option_reason", "No top-option explanation."))

    st.markdown("**Ranked mitigation options**")
    for option in agent_review.get("ranked_options", []):
        st.markdown(f"{option.get('rank', '-')}. **{option.get('title', 'Untitled')}** (score={option.get('score', 0)})")
        st.write(option.get("description", ""))
        st.caption(f"Rationale: {option.get('rationale', '')}")
        st.caption(f"Benefit: {option.get('expected_benefit', '')}")
        st.caption(f"Trade-off: {option.get('tradeoff_note', '')}")


_init_session_state()

st.set_page_config(page_title="Environmental Negotiation MVP", layout="wide")
st.title("AI-Powered Environmental Decision Support (MVP)")
st.write(
    "Phase 2 workflow: parse input, confirm normalized state, run baseline, then run explicit agent review."
)

backend_url = st.text_input("Backend URL", value=DEFAULT_BACKEND_URL).rstrip("/")

st.subheader("Step A: Select input mode")
input_mode = st.selectbox("Select input mode", ["manual_form", "pasted_brief", "uploaded_json"], index=0)
raw_payload = _build_raw_payload(input_mode)

if st.button("Submit to intake parser", type="primary"):
    if input_mode == "uploaded_json" and not raw_payload:
        st.error("Upload a valid JSON file before submitting.")
    elif input_mode == "pasted_brief" and not str(raw_payload).strip():
        st.error("Paste a brief before submitting.")
    else:
        intake_data = _post(
            backend_url,
            "/api/v1/intake/parse",
            {"input_mode": input_mode, "payload": raw_payload},
        )
        if intake_data is not None:
            st.session_state.intake_response = intake_data
            st.session_state.normalized_state = intake_data["project_state"]
            st.session_state.editable_state_json = json.dumps(intake_data["project_state"], indent=2)
            st.session_state.confirmed = False
            st.session_state.baseline_response = None
            st.session_state.agent_review_response = None

if st.session_state.intake_response:
    intake_data = st.session_state.intake_response
    project_state = st.session_state.normalized_state

    st.divider()
    st.subheader("Step C: Review normalized project state")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Site**")
        st.json(project_state.get("site", {}))
        st.markdown("**Building**")
        st.json(project_state.get("building", {}))
    with c2:
        st.markdown("**Constraints**")
        st.json(project_state.get("constraints", {}))
        st.markdown("**Priorities**")
        st.json(project_state.get("priorities", {}))

    _render_validation_issues(intake_data.get("validation_issues", []))

    st.subheader("Assumptions")
    st.write(intake_data.get("assumptions", []) or ["No assumptions recorded."])

    _render_provenance(intake_data.get("provenance", {}))

    st.subheader("Parse metadata")
    st.json(intake_data.get("parse_metadata", {}))

    st.subheader("Edit and resubmit normalized state")
    st.caption("Optional: edit canonical JSON if parser output needs correction, then confirm.")
    st.session_state.editable_state_json = st.text_area(
        "Normalized ProjectState JSON",
        value=st.session_state.editable_state_json,
        height=280,
    )

    if st.button("Apply edited normalized state"):
        try:
            edited = json.loads(st.session_state.editable_state_json)
            validated = ProjectState.model_validate(edited)
            st.session_state.normalized_state = validated.model_dump()
            st.session_state.confirmed = False
            st.session_state.baseline_response = None
            st.session_state.agent_review_response = None
            st.success("Edited state applied. Re-confirm before baseline analysis.")
        except Exception as error:
            st.error(f"Edited state is invalid: {error}")

    st.subheader("Step D: Confirmation gate")
    st.session_state.confirmed = st.checkbox(
        "I confirm this normalized project state is ready for baseline analysis.",
        value=st.session_state.confirmed,
    )

    st.subheader("Step E: Run baseline analysis")
    if st.button("Run baseline analysis", disabled=not st.session_state.confirmed):
        baseline_data = _post(
            backend_url,
            "/api/v1/analysis/baseline",
            {"confirmed": True, "project_state": st.session_state.normalized_state},
        )
        if baseline_data is not None:
            st.session_state.baseline_response = baseline_data
            st.session_state.agent_review_response = None

if st.session_state.baseline_response:
    result_state = st.session_state.baseline_response["project_state"]

    st.divider()
    _render_baseline(result_state)

    st.subheader("Step G: Run agent review")
    if st.button("Run agent review"):
        review_data = _post(
            backend_url,
            "/api/v1/analysis/agent-review",
            {"project_state": result_state},
        )
        if review_data is not None:
            st.session_state.agent_review_response = review_data

if st.session_state.agent_review_response:
    st.divider()
    _render_agent_review(st.session_state.agent_review_response)
