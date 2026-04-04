# Environmental Design Negotiation MVP

AI-powered, web-first decision support for early-stage architectural environmental trade-offs.

## Problem Statement
Early-stage architects often lack fast, explainable environmental feedback while constraints are still being negotiated. Existing workflows are either too slow, too opaque, or too optimization-centric for real-world constraint-heavy decisions.

## Solution Summary
This MVP provides a **constraint-aware negotiation workflow**:
- normalize project inputs,
- validate weak/conflicting assumptions,
- run a baseline environmental heuristic,
- run an explicit agent review,
- compare penalties, deltas, and ranked mitigations.

## What Makes It Agentic
The system exposes a visible, deterministic agent pipeline after baseline:
- **Constraint Agent**: applies hard-constraint penalties
- **Compensation Agent**: proposes up to 3 grounded mitigations
- **Trade-off Agent**: ranks options using user priorities with rationale

This is intentionally transparent and non-magical (no hidden autonomous loop).

## Architecture Overview
- **Frontend**: Streamlit multi-step workflow (A → H)
- **Backend**: FastAPI with stable response contracts
- **Shared schema**: canonical `ProjectState` (Pydantic)
- **Services/agents**: modular, lightweight, deterministic heuristics

## Input Workflow (Step-by-step)
1. **A** Select input mode (`manual_form`, `pasted_brief`, `uploaded_json`)
2. **B** Submit raw input to intake parser
3. **C** Review normalized state, validation, assumptions, provenance
4. **D** Confirm normalized state
5. **E** Run baseline analysis
6. **F** Review baseline metrics/context
7. **G** Run agent review
8. **H** Review constrained deltas and ranked mitigation options

## Tech Stack
- Python
- FastAPI
- Streamlit
- Pydantic
- Pytest
- Claude-ready integration points (optional)
- Open-Meteo-ready integration points (optional)

## Run Locally
1. Create and activate a virtual environment
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run backend:
   - `uvicorn backend.main:app --reload`
4. Run frontend (new terminal):
   - `streamlit run frontend/app.py`
5. Run tests:
   - `pytest -q`

## Demo Flow (A → H)
Use manual form input, run intake, inspect validation/provenance, confirm, run baseline, then run agent review and present ranked options plus penalty deltas.

## Current Limitations
- Baseline and ranking remain heuristic (not simulation-grade)
- Pasted brief parsing is intentionally lightweight
- JSON edit path is flexible but less guided for non-technical users
- No Rhino/BIM ingestion, database, auth, or deployment pipeline yet

## Future Roadmap
- Rhino/Grasshopper integration via backend API
- Better brief parsing with stronger extraction confidence per field
- Optional real API integrations (Open-Meteo, LLM providers)
- Richer decision UX (scenario comparison and stakeholder review)

## Mock Mode
App runs with no API keys:
- `MOCK_MODE=true`, or
- no `ANTHROPIC_API_KEY` and no `OPENAI_API_KEY`

See `.env.example` for environment variables.
