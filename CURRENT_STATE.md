# Current Application State (Phase 5)

Last updated: 2026-04-07

## 1) Snapshot
The repository is in Phase 5 status: project workspace plus interpreted free-text constraint loop.

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
- Full automated test suite passes.

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
- Projects:
  - GET /api/v1/projects
  - POST /api/v1/projects
  - GET /api/v1/projects/{project_id}
  - PUT /api/v1/projects/{project_id}
  - POST /api/v1/projects/{project_id}/runs
  - GET /api/v1/projects/{project_id}/runs

### File-backed persistence
Implemented through backend/services/project_service.py.

Default storage location:
- data/projects

Per-project structure:
- project_meta.json
- current_state.json
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
web/ (Next.js) now provides the primary onboarding + workspace experience:
- Sidebar:
  - project listing and selection
  - run history selection
- Main area:
  1. Guided onboarding and project creation
  2. Design state editing
  3. Constraint editing (structured + free-text)
  4. Save current state
  5. Run baseline + agent review + persist run snapshot
  6. Results and recommendations panel
  7. What Changed view
- API calls are centralized in web/lib/api-client.ts and reused across onboarding/workspace components.

### Frontend fallback/debug UX
- frontend/app.py (Streamlit) remains available for fallback workflow and backend contract debugging.

### Constraint input modes
- Structured mode:
  - constraints.hard_constraints
  - constraints.soft_constraints
- Written mode:
  - constraints.free_text
- Interpreted mode:
  - project_state.parsed_constraints.extracted_items
  - item statuses: proposed, accepted, edited, rejected
  - unresolved_items, confidence_label/score, parser_provider/mode, notes, conflict_warnings
- Both manual structured constraints and interpreted constraints can be used together and are persisted in project state.

Precedence and conflict behavior:
- Manual hard constraints remain authoritative.
- Accepted/edited parsed items are appended as supplemental effective hard constraints.
- Effective analysis context is exposed as constraints.effective_hard_constraints.
- Conflicts are surfaced in parsed_constraints.conflict_warnings and assumptions.

## 3) Climate Layer Status
Still active and integrated into every run cycle:
- Visual Crossing primary weather provider
- Open-Meteo geocoding
- Open-Meteo weather fallback
- Mock final fallback

Climate transparency fields remain exposed:
- climate_context.provider
- climate_context.source_tier

## 4) Configuration and Secrets
- .env is local-only and gitignored.
- .env.example remains template-only (no real keys).

Supported env vars include:
- APP_ENV
- MOCK_MODE
- VISUAL_CROSSING_API_KEY
- OPEN_METEO_BASE_URL
- PROJECTS_DATA_DIR
- optional LLM keys: ANTHROPIC_API_KEY and OPENAI_API_KEY

## 5) LLM and Constraint Interpretation Status

### Implemented now
- Centralized config exposes both LLM keys via backend/core/config.py settings.
- Local .env loading through config is active and does not override process env.
- backend/services/llm_service.py now provides:
  - key presence detection helpers
  - provider availability/selection logic
  - provider-backed free-text constraint interpretation requests (Anthropic/OpenAI)
  - strict JSON extraction/validation for parsed constraint outputs
- backend/services/constraint_parsing_service.py now provides:
  - LLM-first interpretation path
  - deterministic heuristic fallback path
  - transparent confidence/unresolved/conflict metadata
  - merge logic for effective hard constraints

### Available but scoped
- Live provider-backed calls are currently scoped to free-text constraint interpretation only.
- Intake mode parsing, baseline narrative generation, and recommendation summarization remain deterministic.

## 6) Testing and Verification
Current tests include:
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
- tests/conftest.py

Latest verification:
- pytest -q result: pending current verification run
- web build result: npm run build passed
- Live smoke checks completed for:
  - backend startup
  - web frontend startup
  - onboarding-equivalent project creation
  - project create/list/get/update
  - run creation and history retrieval
  - iterative rerun diff presence
  - free-text constraint persistence in run input state
  - interpretation endpoint and parsed-constraint persistence

## 7) Current Product Boundaries
Intentionally not implemented in this phase:
- auth/accounts
- cloud database
- collaboration/multiplayer
- canvas-style editor
- Rhino/IFC/BIM ingestion
- full simulation engine
- autonomous agent loops

## 8) Known Limitations
- Persistence is local file-based only.
- Diff view is intentionally simple and key-based.
- Environmental scoring remains heuristic.
- No branchable scenario tree yet (single current state per project).
- No conflict resolution for concurrent edits.
- LLM integration remains readiness-only; no live provider-backed text generation in main workflows.
- Interpretation quality is bounded by provider response quality or heuristic coverage.

## 9) Run Instructions
Backend:
- uvicorn backend.main:app --reload

Main frontend:
- cd web
- npm install
- npm run dev

Fallback frontend:
- streamlit run frontend/app.py

Tests:
- pytest -q

## 10) Next Suggested Phase
Scenario branching and comparative decision views:
- multiple named alternatives per project
- side-by-side run comparison
- trend charts across runs
- stronger climate confidence metadata in UI
