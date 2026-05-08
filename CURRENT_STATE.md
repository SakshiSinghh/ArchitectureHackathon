# Current Application State (Phase 7)

Last updated: 2026-05-09

## 1) Snapshot
The repository is in Phase 7 status: Orientation Options feature added on top of Phase 6 (Review Mode floor plan upload).

What is currently true:
- FastAPI backend remains the source of truth.
- Next.js frontend in web/ is now the main product-facing UI.
- Streamlit frontend remains available as fallback/debug tooling.
- Web frontend uses a centralized typed API service layer mapped to existing backend routes.
- Climate provider architecture from Phase 3 remains active.
- The app now supports projects as first-class persisted workspaces.
- Current design state is editable and saveable per project.
- Baseline and agent review can be rerun repeatedly as negotiation cycles.
- Run snapshots are stored and history is visible.
- A simple What Changed comparison is available between the latest and previous run.
- Free-text constraints can now be interpreted into structured candidates with confidence and unresolved tracking.
- Users can accept, edit, or reject interpreted constraints in onboarding and workspace flows.
- Accepted/edited interpreted constraints are persisted and merged into effective hard-constraint context with transparent precedence.
- Floor plan images and PDFs can be uploaded for AI-assisted environmental analysis (Review Mode).
- Full automated test suite passes (45 tests).
- Three scored orientation options are now generated after each Run Analysis.
- SVG top-down building diagram (compass rose + colour-coded facades) renders per orientation.
- Full automated test suite passes (54 tests).

## 2) Implemented Scope

### Backend API
- Health:
  - GET /health
- Intake:
  - GET /api/v1/intake/ping
  - POST /api/v1/intake/parse
  - POST /api/v1/intake/interpret-constraints
- Analysis:
  - GET /api/v1/analysis/ping
  - POST /api/v1/analysis/baseline
  - POST /api/v1/analysis/agent-review
  - POST /api/v1/analysis/orientation-options  <- NEW (Phase 7)
- Projects:
  - GET /api/v1/projects
  - POST /api/v1/projects
  - GET /api/v1/projects/{project_id}
  - PUT /api/v1/projects/{project_id}
  - POST /api/v1/projects/{project_id}/runs
  - GET /api/v1/projects/{project_id}/runs
  - POST /api/v1/projects/{project_id}/upload-plan  <- NEW (Phase 6)

### Review Mode - floor plan upload (Phase 6)
Implemented through:
- backend/agents/floor_plan_agent.py
- backend/services/floor_plan_service.py
- backend/services/llm_service.py (vision methods added)
- shared/project_state.py (RoomAnalysis, FloorPlanAnalysis schemas added)

Accepted file types: JPEG, PNG, GIF, WebP, PDF.

Pipeline:
1. File uploaded via POST /api/v1/projects/{project_id}/upload-plan
2. FloorPlanAgent sends image/PDF to Claude vision API (claude-sonnet-4-6)
3. Claude extracts rooms, facade orientations, environmental issues, element-level suggestions
4. FloorPlanService merges inferred orientation_deg and window_to_wall_ratio into
   project Building fields (only fills blanks, does not overwrite user-supplied values)
5. Full FloorPlanAnalysis persisted in project current_state.floor_plan_analysis
6. Provenance tracks which building fields were inferred from the floor plan

Fallback behaviour:
- MOCK_MODE=true or no ANTHROPIC_API_KEY returns deterministic mock analysis
- LLM call failure returns graceful fallback with error note in analysis_notes

### File-backed persistence
Implemented through backend/services/project_service.py.

Default storage location:
- data/projects

Per-project structure:
- project_meta.json
- current_state.json (now includes floor_plan_analysis field)
- runs/{run_id}.json

### Iteration model
Each run snapshot captures:
- run_id and timestamp
- input_state used for that run
- baseline_state after climate-informed baseline pipeline
- agent_review response
- top recommendation
- climate provider and source tier metadata

What Changed support captures:
- changed input fields (flattened keys)
- changed baseline metrics
- changed top recommendation
- changed agent metric deltas

### Frontend workspace UX (main)
web/ (Next.js) provides the primary onboarding + workspace experience.
- Sidebar: project listing and selection, run history selection
- Main area: onboarding, design state editing, constraint editing, save, run, results, What Changed view
- API calls centralized in web/lib/api-client.ts
- Floor plan upload UI is wired into the Next.js workspace center panel (file picker, drag-and-drop, results panel with room breakdown).

### Constraint input modes
- Structured mode: constraints.hard_constraints, constraints.soft_constraints
- Written mode: constraints.free_text
- Interpreted mode: parsed_constraints.extracted_items with accept/edit/reject statuses
- Both manual and interpreted constraints can be used together.


### Orientation Options – Design Mode (Phase 7)
Implemented through:
- backend/services/orientation_service.py (new)
- backend/schemas/api_models.py (OrientationOption, OrientationOptionsResponse schemas)
- backend/api/routes/analysis.py (POST /orientation-options endpoint)
- web/lib/api-types.ts (OrientationOption, OrientationOptionsResponse types)
- web/lib/api-client.ts (getOrientationOptions() function)
- web/components/workspace/orientation-diagram.tsx (new SVG component)
- web/components/workspace/orientation-options.tsx (new 3-card component)
- web/components/workspace/workspace.tsx (orientationOptions state + handleRun wiring)
- web/components/workspace/right-panel.tsx (renders OrientationOptions in Insights panel)
- tests/test_orientation.py (9 new tests, all pass)

Feature behaviour:
- After Run Analysis, the app sweeps all 8 compass orientations (N/NE/E/SE/S/SW/W/NW)
- Climate data is fetched once and reused across all 8 sweep variants
- Each variant gets a composite score: daylight*w + ventilation*w - energy_risk*w (weighted by project priorities)
- Top 3 are returned; user's current orientation always included even if outside top 3
- Each option shows: rank badge, label (e.g. "South-East"), orientation in degrees, composite score
- SVG diagram shows compass rose, dashed sun arc (E to W through south), building rectangle rotated to the orientation, facade colours (west=orange, south=yellow, east=peach, north=blue)
- Narrative sentence generated per option (LLM if available, heuristic fallback)
- Orientation Options card appears in the right-panel Insights section

## 3) Climate Layer Status
Still active and integrated into every run cycle:
- Visual Crossing primary weather provider
- Open-Meteo geocoding and weather fallback
- Mock final fallback

## 4) Configuration and Secrets
- .env is local-only and gitignored.
- .env.example remains template-only.

Supported env vars:
- APP_ENV, MOCK_MODE
- VISUAL_CROSSING_API_KEY, OPEN_METEO_BASE_URL
- PROJECTS_DATA_DIR
- ANTHROPIC_API_KEY (required for live floor plan vision and constraint interpretation)
- OPENAI_API_KEY (optional, constraint interpretation only)

## 5) LLM Status

### Live LLM calls
- Free-text constraint interpretation: Anthropic or OpenAI
- Floor plan vision analysis: Anthropic only (claude-sonnet-4-6)
- Baseline narrative insight (narrative_insight in BaselineResults): Anthropic or OpenAI
- Agent review top-option reason and penalty summary: Anthropic or OpenAI

### Still deterministic
- Intake mode parsing
- Heuristic metric scores (energy_risk, daylight_potential, ventilation_potential)
- Mitigation option candidates and trade-off ranking

## 6) Testing and Verification
Current tests:
- tests/test_health.py
- tests/test_intake.py
- tests/test_validation.py
- tests/test_analysis.py
- tests/test_provenance.py
- tests/test_climate_layer.py
- tests/test_config_loading.py
- tests/test_llm_readiness.py
- tests/test_constraint_parsing.py
- tests/test_constraint_interpretation.py
- tests/test_projects.py
- tests/test_floor_plan.py  <- NEW (Phase 6)
- tests/conftest.py

Latest verification:
- pytest -q result: 45 passed, 0 failed
- 14 new floor plan tests: agent unit, orientation inference, full API integration

## 7) Current Product Boundaries
Intentionally not implemented:
- auth/accounts
- cloud database
- collaboration/multiplayer
- canvas-style editor
- Rhino/IFC/BIM ingestion
- full simulation engine
- autonomous agent loops
- OpenAI provider for vision (Anthropic only)

## 8) Known Limitations
- Persistence is local file-based only.
- Diff view is intentionally simple and key-based.
- Environmental scoring remains heuristic.
- No branchable scenario tree yet.
- No conflict resolution for concurrent edits.
- Floor plan orientation and WWR inference is approximate, not BIM-grade.

## 9) Run Instructions
Backend:
- uvicorn backend.main:app --reload

Main frontend:
- cd web and npm install and npm run dev

Fallback frontend:
- streamlit run frontend/app.py

Tests:
- pytest -q

## 10) Next Suggested Phase
- Scenario branching: multiple named alternatives per project, side-by-side run comparison
- Wire LLM generation into baseline narrative and agent review summaries
