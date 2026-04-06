# Environmental Design Negotiation Workspace

A web-first decision-support app for early-stage architectural negotiation where the core unit is a saved, evolving design state.

## Product Direction
The app is now project-centered rather than one-shot form-centered.

Users can:
- create projects
- save and load current design states
- iteratively update intent, constraints, and priorities
- rerun baseline and agent review cycles
- inspect run history and compare what changed

## Current Architecture
- Frontend (main): Next.js app in web/
- Frontend (fallback/debug): Streamlit app in frontend/
- Backend: FastAPI API
- Canonical model: ProjectState in shared schema
- Persistence: local file-backed project storage under data/projects
- Climate layer: Visual Crossing primary, Open-Meteo fallback/geocoding, deterministic mock fallback

## Frontend Integration Status
- Vercel v0 generated UI is integrated as the main product-facing frontend in web/.
- Backend remains the source of truth for projects, state updates, runs, and diffs.
- Streamlit remains available for fallback debugging and contract inspection.

Integrated user flow in web/:
- guided onboarding and project creation
- project selection and workspace editing
- save current state
- run baseline and agent-review flow with persisted run snapshots
- run history browsing
- What Changed view

Constraint input modes:
- Structured constraints: hard_constraints and soft_constraints
- Written constraints: constraints.free_text
- Interpreted constraints: parsed_constraints.extracted_items with accept/edit/reject statuses
- Both manual and interpreted constraints can be used together.
- Free-text constraints can be interpreted through a dedicated endpoint and reviewed in UI.
- Accepted/edited interpreted constraints are merged into effective_hard_constraints for analysis.

## API Surface
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
- Projects (Phase 4):
  - GET /api/v1/projects
  - POST /api/v1/projects
  - GET /api/v1/projects/{project_id}
  - PUT /api/v1/projects/{project_id}
  - POST /api/v1/projects/{project_id}/runs
  - GET /api/v1/projects/{project_id}/runs

## Local Persistence Model
Default storage path:
- data/projects

Structure:
- data/projects/{project_id}/project_meta.json
- data/projects/{project_id}/current_state.json
- data/projects/{project_id}/runs/{run_id}.json

Each run snapshot stores:
- input state used for the cycle
- baseline-enriched state
- agent-review output
- top recommendation
- climate provider/source metadata

## Climate Provider Stack
- Primary weather provider: Visual Crossing using VISUAL_CROSSING_API_KEY
- Geocoding: Open-Meteo geocoding API
- Weather fallback: Open-Meteo forecast API
- Final fallback: deterministic mock provider

Source transparency in baseline state:
- climate_context.provider
- climate_context.source_tier

## Workspace Flow
1. Create or select a project in the sidebar.
2. Edit current design state in grouped sections.
3. Save current state.
4. Run baseline + agent review cycle.
5. Inspect results and recommendations.
6. Review What Changed against the previous run.
7. Continue iterating.

## Configuration
Use a local .env file for secrets and overrides. Do not commit .env.

Environment variables:
- APP_ENV
- MOCK_MODE
- VISUAL_CROSSING_API_KEY
- OPEN_METEO_BASE_URL
- PROJECTS_DATA_DIR
- ANTHROPIC_API_KEY (optional)
- OPENAI_API_KEY (optional)

Frontend web/ environment:
- copy web/.env.local.example to web/.env.local
- set NEXT_PUBLIC_API_BASE_URL to backend URL (default http://127.0.0.1:8000)

Template values live in .env.example.

## Run Locally
1. Create and activate a virtual environment.
2. Install dependencies:
   - pip install -r requirements.txt
3. Install web frontend dependencies:
  - cd web
  - npm install
  - cd ..
4. Ensure local .env exists and contains VISUAL_CROSSING_API_KEY.
5. Optionally set ANTHROPIC_API_KEY and/or OPENAI_API_KEY for future provider-backed LLM features.
6. Run backend:
   - uvicorn backend.main:app --reload
7. Run main frontend:
  - cd web
  - npm run dev
8. Optional fallback frontend:
   - streamlit run frontend/app.py
9. Run tests:
   - pytest -q

## Current Development Status
Implemented now:
- project workspace and project persistence
- editable current design state
- iterative run cycle with snapshots
- run history listing
- simple What Changed diff against previous run
- climate-informed baseline and climate-grounded agent explanations
- free-text constraint interpretation with LLM-first + heuristic fallback
- human-in-loop accept/edit/reject flow for interpreted constraints
- transparent precedence and conflict warnings between manual and parsed constraints

Still simplified:
- no user accounts/auth
- no cloud database or collaboration
- no canvas-style geometry editing
- no full simulation engine
- environmental scoring remains heuristic (not simulation-grade)

## Next Product Step
A strong next phase is scenario management: branchable design alternatives per project, side-by-side run comparison, and richer trend visualizations across iterations.
