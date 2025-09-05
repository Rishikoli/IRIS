# IRIS RegTech Platform

Intelligent Risk & Investigation System for detecting, explaining, and forecasting fraud chains affecting retail investors in India.

## Project Structure

```
iris-regtech-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application
│   │   ├── database.py     # Database configuration
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── crud.py         # Database operations
│   │   └── routers/        # API endpoints
│   ├── requirements.txt    # Python dependencies
│   ├── run.py             # Development server
│   └── .env.example       # Environment variables template
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── App.tsx        # Main app component
│   │   └── main.tsx       # Entry point
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Vite configuration
└── README.md              # This file
```

## Features

- **Tip Risk Analysis**: AI-powered analysis of investment tips for fraud detection
- **Advisor Verification**: SEBI registration verification for financial advisors
- **Document Authentication**: PDF authenticity checking with OCR and AI analysis
- **Regulatory Dashboard**: Real-time fraud monitoring and visualization
- **Risk Forecasting**: AI-powered predictions of fraud hotspots
- **Human-in-the-Loop Review**: Manual review and override of AI decisions

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Database (for demo - PostgreSQL recommended for production)
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: UI library with TypeScript
- **Vite**: Build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Lucide React**: Icon library

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Run the development server:
   ```bash
   python run.py
   ```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database

The application uses SQLite for development with the following core entities:
- **Tips**: Investment tips submitted for analysis
- **Assessments**: AI risk assessments of tips
- **PDF Checks**: Document authenticity verification results

The database file (`iris_regtech.db`) will be created automatically when you first run the backend.

## Development Status

This is the initial project setup with core infrastructure. The following features are implemented:

✅ **Completed:**
- FastAPI backend with CORS middleware
- React frontend with TypeScript and Tailwind CSS
- SQLite database with SQLAlchemy models
- Basic CRUD operations for core entities
- Responsive navigation and routing
- API service layer

🚧 **In Progress:**
- Individual feature implementations (tip analysis, advisor verification, etc.)

## Contributing

This is a demonstration project for the IRIS RegTech platform. Future tasks will implement the specific features outlined in the requirements.

## Comprehensive Guide

### Architecture
- Backend: FastAPI + SQLAlchemy ORM + SQLite (dev)
- Frontend: React 18 + TypeScript + Vite + Tailwind CSS
- Security: CORS, security headers, input validation, standardized exceptions
- AI Integration: Gemini 2.0 Flash API (where applicable)

### Core Feature Areas
- Tip Risk Analysis, Advisor Verification, PDF Authentication
- Regulatory Dashboard with Heatmaps (sector/region)
- Risk Forecasting
- Fraud Chain Detection (graph visualization + details modal)
- Human-in-the-Loop Review
- Multi-Source Data Integration (FMP, Google Trends, Economic Times)
- Real-time Updates (WebSocket)

---
 
## Quick Start
 
### Option A: Docker Compose (recommended)
Requires Docker Desktop.
 
```bash
# From repo root
docker compose up --build
```
 
Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
 
### Option B: Local Dev
 
Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python run.py
# API: http://localhost:8000
```
 
Frontend
```bash
cd frontend
npm install
npm run dev
# App: http://localhost:3000
```
 
---

## System Architecture Diagram

```text
┌──────────────────────────────┐        HTTP/WS        ┌──────────────────────────────┐
│  Frontend (React + Vite)     │  <------------------>  │  Backend (FastAPI)           │
│  - UI (Tailwind CSS)         │                        │  - Routers (REST/WS)         │
│  - Fraud Chain Graph/Modal   │                        │  - CRUD + Services           │
│  - Dashboard & Reviews       │                        │  - AI Integrations           │
└──────────────┬───────────────┘                        └──────────────┬───────────────┘
               │                                                        │
               │                                                        │ SQL/Cache
               ▼                                                        ▼
        ┌───────────────┐                                      ┌────────────────┐
        │  Redis (opt)  │                                      │ PostgreSQL DB  │
        │  Caching      │                                      │ (prod-ready)   │
        └───────────────┘                                      └────────────────┘
```

## How It Works (High-Level Flow)

- __Tip Ingestion__: User submits an investment tip. Stored in `Tips`.
- __AI Risk Analysis__: Backend invokes AI analysis to score risk; result saved in `Assessments` and linked to the tip.
- __Advisor Verification__: Advisor IDs checked against SEBI registry; stored for audits.
- __PDF Authentication__: Document OCR + authenticity checks; stored in `PDFChecks`.
- __Fraud Chain Detection__: Related tips/entities connected into a graph for exploration.
- __Human-in-the-Loop Review__: Analysts review AI outcomes, override/confirm, and add notes in `Reviews`.
- __Dashboards & Notifications__: Frontend renders real-time visuals; server may push updates via WebSocket.

## Human-in-the-Loop Review

- __Reviewer Actions__: Approve/reject AI flags, adjust risk levels, annotate cases.
- __Traceability__: All overrides are persisted for auditability and model feedback.
- __UI__: Accessible modals and review panels with keyboard support and clear status badges.

## AI Components

- __Gemini 2.0 Flash__ for natural-language risk reasoning and summaries.
- __OCR & NLP Pipelines__ for PDF extraction and authenticity cues.
- __Heuristics/Rules__ aiding sector/region mapping and correlation.

---

## PostgreSQL Setup

You can run PostgreSQL via Docker (recommended) or install it locally.

### Option A: Docker Compose
 - Already configured in `docker-compose.yml` as service `postgres` with:
  - DB: `irisdb`
  - User: `iris`
 - The backend uses `DATABASE_URL=postgresql+psycopg://iris:<DB_PASSWORD>@postgres:5432/irisdb` in Compose (set via environment variables).

Bring everything up:
```bash
docker compose up --build
```

### Option B: Local PostgreSQL
1) Install PostgreSQL 15+
2) Create a database and user:
```sql
CREATE DATABASE irisdb;
CREATE USER iris WITH PASSWORD '<DB_PASSWORD>';
GRANT ALL PRIVILEGES ON DATABASE irisdb TO iris;
```
3) Set backend env var before starting the API (do not commit secrets):
```powershell
$env:DATABASE_URL = "postgresql+psycopg://iris:<DB_PASSWORD>@localhost:5432/irisdb"
python backend/run.py
```

### Initialize Schema
Apply schema if needed (example via psql):
```powershell
psql -h localhost -U iris -d irisdb -f backend/schema/postgres.sql
```

Notes:
- In Docker, the backend waits for Postgres healthcheck before starting.
- Ensure ports `5432` (Postgres) and `8000/3000` (backend/frontend) are free.
 
## Fraud Chain UI
 
Key files:
- `frontend/src/components/FraudChainGraph.tsx` (Cytoscape-based)
- `frontend/src/components/FraudChainVisualization.tsx` (D3-based)
- `frontend/src/components/FraudChainDetailsModal.tsx` (Details modal)
 
Features:
- Zoom, Fit, Export PNG controls overlay in `FraudChainGraph.tsx`.
- Node styles with readable labels; tip labels monospace; assessment labels high-contrast.
- Details modal supports Esc/backdrop close, ARIA roles, scroll lock.
- Glassmorphism styling across header, body, metadata/reference cards, and footer for dark theme.
 
Styling notes (Tailwind):
- Glass: `bg-white/10 backdrop-blur-xl border border-white/20 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.15)]`
- Text on glass: `text-white/80` to `text-white/90`
- Dark-themed buttons and primary accent for export.
 
---
 
## Troubleshooting
 
### Heatmap 503 (Service Unavailable)
Symptoms: 503 from `/api/fraud-heatmap` when loading dashboard.
 
Checklist:
- Ensure backend is running at http://localhost:8000 and frontend proxy targets `/api/*`.
- Seed data: POST `/api/populate-sample-heatmap-data`.
- Verify `from_date <= to_date` and reasonable span.
- Backend fixes included:
  - Corrected date bucket construction in `aggregate_heatmap_data()`.
  - Safer sector filtering via `Tip.message.contains()`.
 
If errors persist, check backend logs around `crud.aggregate_heatmap_data()` and share the stack trace.
 
### Frontend build issues
- Remove `frontend/node_modules` and reinstall.
- Restart Vite dev server; clear cache if necessary.
 
---
 
## Scripts
- `backend/scripts/seed_demo_data.py`: populate demo entities.
- Heatmap demo via `/api/populate-sample-heatmap-data` and `/api/generate-realtime-data`.
 
---
 
## Deployment
 
### Docker
```bash
docker compose up --build -d
```
 
### Manual
- Backend: `python run.py` or Uvicorn/Gunicorn
- Frontend: `npm run build` and serve via Nginx (see `frontend/nginx.conf`)
 
Environment:
- Configure CORS, API base URL, and any API keys (e.g., Gemini) via `.env` files.
 
---
 
## API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
 
---
 
## License
 
This project is for demonstration purposes only.