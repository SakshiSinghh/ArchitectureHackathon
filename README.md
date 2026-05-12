# ArchEnv — Environmental Intelligence for Architects

A decision-support app for early-stage architectural design. Architects describe a building project, run environmental analysis, and get AI-ranked design recommendations with orientation scoring, energy risk, daylight potential, and ventilation performance.

## Live Demo

- **Frontend:** [architecture-hackathon.vercel.app](https://architecture-hackathon.vercel.app)
- **Backend API:** [precious-magic-production-805e.up.railway.app](https://precious-magic-production-805e.up.railway.app)

## Features

- **Project workspace** — create, save, and iterate on design states
- **Environmental analysis** — heuristic baseline scoring for energy risk, daylight, ventilation, and heat exposure
- **AI recommendations** — Claude-powered ranked design options with trade-off notes
- **Orientation comparison** — ranked orientations for your location with per-metric scores and narrative
- **Constraint management** — free-text AI interpretation with accept / edit / reject review flow
- **Run history** — browse past analysis runs and compare what changed
- **PDF export** — one-click export of the Insights tab as a PDF report
- **Grasshopper plugin** — GHPython component that calls the backend from Rhino/Grasshopper

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, shadcn/ui, Tailwind CSS 4 |
| Backend | FastAPI, Python 3.13 |
| AI | Anthropic Claude (optional — falls back to heuristics) |
| Climate | Visual Crossing (primary), Open-Meteo (fallback), mock (final fallback) |
| Hosting | Vercel (frontend) + Railway (backend) |

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in your keys
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd web
npm install
# create web/.env.local with:
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment Variables

### Backend (`.env`)

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key (optional — uses heuristics if absent) |
| `VISUAL_CROSSING_API_KEY` | Weather data (optional — falls back to Open-Meteo) |
| `MOCK_MODE` | Set `true` to skip all external API calls |
| `PROJECTS_DATA_DIR` | Override data storage path (default: `data/projects`) |

### Frontend (`web/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Backend URL (default: `http://localhost:8000`) |

## Deployment

### Backend → Railway

1. Connect your GitHub repo in Railway
2. Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables (at minimum `ANTHROPIC_API_KEY`)

### Frontend → Vercel

1. Import repo in Vercel
2. Set **Root Directory** to `web`, **Framework** to Next.js
3. Add env var `NEXT_PUBLIC_API_BASE_URL` pointing to your Railway URL

## API Endpoints

```
GET  /health
GET  /api/v1/intake/ping
POST /api/v1/intake/parse
POST /api/v1/intake/interpret-constraints
POST /api/v1/analysis/baseline
POST /api/v1/analysis/agent-review
GET  /api/v1/analysis/orientation-options
GET  /api/v1/projects
POST /api/v1/projects
GET  /api/v1/projects/{project_id}
PUT  /api/v1/projects/{project_id}
POST /api/v1/projects/{project_id}/runs
GET  /api/v1/projects/{project_id}/runs
POST /api/v1/projects/{project_id}/upload-plan
```

## Grasshopper Plugin

Download the GHPython component from the **Grasshopper** tab in the app. Connects orientation slider → live environmental scores without leaving Rhino. Works with Rhino 7 (IronPython) and Rhino 8 (CPython). No extra plugins needed.

## Project Structure

```
├── backend/          FastAPI app
│   ├── api/          Route handlers
│   ├── agents/       Claude-based agent logic
│   ├── models/       Pydantic schemas
│   └── main.py       App entry point
├── web/              Next.js frontend
│   ├── app/          Pages and layout
│   ├── components/   UI components
│   └── lib/          API client and types
├── data/             Local project storage (git-ignored)
├── requirements.txt  Python dependencies
└── .env.example      Environment variable template
```

## Known Limitations

- No user auth — all projects are shared on a single backend instance
- Environmental scoring is heuristic, not simulation-grade
- Data is stored on the filesystem (resets on Railway redeploy unless a volume is attached)
