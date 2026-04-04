# Current Application State (Phase 2)

Last updated: 2026-04-04

## 1) Snapshot
The repository is in **Phase 2 (credible agentic MVP)** status.

What is currently true:
- Web-first architecture remains in place (FastAPI backend + Streamlit frontend).
- Frontend and backend are fully wired for intake, baseline, and agent-review stages.
- Inputs normalize into canonical `ProjectState` with explicit provenance categories.
- Human-in-the-loop confirmation remains required before baseline analysis.
- Mock/demo mode still works with no API keys.
- Agent behavior is visible and deterministic (constraint → compensation → trade-off).
- Full test suite currently passes.

## 2) Implemented Scope

### Backend (FastAPI)
Implemented in `backend/`:
- Health:
  - `GET /health`
- Intake:
  - `GET /api/v1/intake/ping`
  - `POST /api/v1/intake/parse`
- Analysis:
  - `GET /api/v1/analysis/ping`
  - `POST /api/v1/analysis/baseline`
  - `POST /api/v1/analysis/agent-review`

Behavior:
- Intake supports:
  - `manual_form`
  - `pasted_brief`
  - `uploaded_json`
- Intake response includes:
  - `project_state`
  - `validation_issues`
  - `assumptions`
  - `provenance`
  - `parse_metadata` (`input_mode`, parser note, confidence, unparsed items)
- Baseline endpoint:
  - requires `confirmed=true`
  - computes heuristic baseline + climate context
- Agent-review endpoint:
  - requires baseline-computed project state
  - returns baseline metrics, constrained metrics, deltas, penalty summary,
    ranked mitigation options, and top-option reason

### Frontend (Streamlit)
Implemented in `frontend/app.py`:
- **Step A**: input mode selection.
- **Step B**: raw input and intake submission.
- **Step C**: normalized-state review (site, building, constraints, priorities).
- Validation issues shown by severity.
- Assumptions and provenance shown explicitly.
- Optional JSON edit/resubmit of normalized state.
- **Step D**: explicit confirmation gate.
- **Step E**: run baseline.
- **Step F**: review baseline metrics + context.
- **Step G**: run explicit agent review.
- **Step H**: inspect deltas and ranked mitigation options.

### Shared Canonical Schema
Implemented in `shared/project_state.py`:
- Canonical `ProjectState` includes:
  - site
  - building
  - constraints
  - priorities
  - provenance
  - assumptions
  - validation issues
  - climate context
  - baseline results
  - mitigation options

Provenance now tracks:
- `user_provided_fields`
- `inferred_fields`
- `defaulted_fields`
- `unresolved_fields`

### Services and Agents
Core services/agents now provide:
- Stronger intake parsing and normalization metadata
- Stronger validation checks (coords, geometry plausibility, priorities quality, constraint conflicts)
- Deterministic baseline scoring
- Explicit post-baseline agent-review pipeline:
  - Constraint Agent: heuristic penalties
  - Compensation Agent: up to 3 grounded mitigation options
  - Trade-off Agent: priority-weighted ranking + score rationale

## 3) Configuration and Secrets

### Environment files
`.env.example` includes empty placeholders:
- `ANTHROPIC_API_KEY=`
- `OPENAI_API_KEY=`
- `OPEN_METEO_BASE_URL=`
- `APP_ENV=`
- `MOCK_MODE=`

### Mock mode
- If keys are missing, app resolves to mock/demo behavior.
- No real keys are required for current end-to-end workflow.

## 4) Testing and Verification

### Test coverage currently present
- `tests/test_health.py`
- `tests/test_intake.py`
- `tests/test_validation.py`
- `tests/test_analysis.py`
- `tests/test_provenance.py`

### Latest verification result
- `pytest -q` result: **12 passed**
- Git publishing check: **main pushed to origin**

## 5) Repository Status (High-Level)
Top-level files:
- `README.md`
- `CURRENT_STATE.md`
- `requirements.txt`
- `.gitignore`
- `.env.example`

Top-level folders:
- `backend/`
- `frontend/`
- `shared/`
- `tests/`

## 6) Intentional MVP Simplifications
Still deliberate for hackathon safety:
- No Rhino/IFC/BIM parsing.
- No simulation engine.
- No database/auth/deployment pipeline.
- No mandatory external APIs.
- No autonomous optimization loop.

## 7) Known Limitations (Current)
- Baseline, penalty, and ranking outputs are heuristic and deterministic.
- Pasted-brief parsing is intentionally lightweight and uncertainty-prone.
- UI normalized-state editing is JSON-based (powerful but not guided).
- Option ranking uses simple weighted math rather than calibrated empirical models.

## 8) Run Instructions (Current)
Backend:
- `uvicorn backend.main:app --reload`

Frontend:
- `streamlit run frontend/app.py`

Tests:
- `pytest -q`

## 9) Risk Notes
Main near-term risk is perceived overconfidence from heuristic outputs. Current implementation reduces this risk by making provenance, validation, parser confidence, and post-baseline deltas explicit in both API contracts and UI.

## 10) Repository Publishing Status
- Git initialized and initial commit created.
- Default branch renamed to `main`.
- Remote configured: `origin = https://github.com/AlvieKun/ArchitectureHackathon.git`.
- Push status: `main` successfully pushed and tracking `origin/main`.
- GitHub web check confirms key files are visible and `README.md` renders correctly.
