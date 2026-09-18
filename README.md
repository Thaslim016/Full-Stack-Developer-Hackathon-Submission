# Darukaa.Earth — Full-Stack Geospatial Carbon & Biodiversity Dashboard

A production-oriented hackathon implementation for managing carbon/biodiversity projects,
drawing geographic sites, viewing sites on an interactive Mapbox map, and inspecting
time-series analytics.

## Architecture

React + Vite + Mapbox GL JS + Chart.js
              │
              ▼
        Flask REST API
              │
       JWT authentication
              │
              ▼
      PostgreSQL + PostGIS
              │
              ▼
 projects ─ sites ─ metrics

The frontend uses React for the dashboard, Mapbox GL JS for polygon drawing and rendering,
and Chart.js for time-series visualization. The backend exposes JWT-protected REST endpoints.
PostGIS stores site geometry as GeoJSON-compatible polygons and supports spatial indexing.

## Database schema

- `users`: id, name, email, password_hash, created_at
- `projects`: id, name, description, status, owner_id, created_at
- `sites`: id, project_id, name, geometry (PostGIS Polygon/MultiPolygon), area_hectares,
  latitude, longitude, created_at
- `metrics`: id, site_id, observed_on, carbon_tco2e, biodiversity_index,
  tree_cover_pct, soil_organic_carbon_pct, rainfall_mm

Relationships:
`users 1─N projects 1─N sites 1─N metrics`

## Local setup

### 1. Start PostGIS

```bash
docker compose up -d db
```

### 2. Backend

```bash
cd backend
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask --app run.py init-db
python run.py
```

Backend: `http://localhost:5000`

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend: `http://localhost:5173`

Set `VITE_MAPBOX_TOKEN` to a Mapbox public token.

### Demo account

The seed command creates:
- email: `demo@darukaa.earth`
- password: `DarukaaDemo123!`

Change this for any real deployment.

## API

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/:id`
- `POST /api/projects/:id/sites`
- `GET /api/sites`
- `GET /api/sites/:id`
- `GET /api/sites/:id/metrics`

All project/site/metric routes require `Authorization: Bearer <JWT>`.

## CI/CD

GitHub Actions runs backend tests and frontend build on every push and pull request.
The repository also includes Husky + lint-staged + Prettier configuration for frontend
commit-time formatting.

For Render deployment, create a PostgreSQL database with PostGIS support, configure
environment variables, deploy the backend as a Python service and frontend as a Node
static site. The included Dockerfiles can also be used by container-based platforms.

## Product decisions / trade-offs

- GeoJSON is used at the API boundary because it is browser-native and works cleanly with Mapbox.
- PostGIS is used for persistence and future spatial queries rather than storing polygons as text.
- Chart.js is kept lightweight for the time-series requirement.
- Analytics are deterministic and transparent: the API returns stored observations and simple
  derived deltas rather than inventing environmental measurements.
- Authentication is JWT-based as required; production deployments should additionally add
  refresh-token rotation, email verification, rate limiting and secret management.

## Required submission links

GitHub repository: `TO BE ADDED`
Live demo: `TO BE ADDED`

Hiring-team access for a private repository:
- ankita.dasgupta@darukaa.com
- harsh.kumar@darukaa.com
- utkarsh.gauniyal@darukaa.com
- guneet.mutreja@darukaa.com
