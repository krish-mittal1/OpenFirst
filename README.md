<div align="center">

# 🚀 OpenFirst

### Find Beginner-Friendly Open Source Projects — Backed by Real Data

OpenFirst analyzes GitHub repositories in real-time to help beginners find **active, welcoming, and well-maintained** open source projects to contribute to.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🎯 The Problem

Beginners struggle to contribute to open source because:

- 🔍 **Hard to find active repos** — many repos with "good first issue" labels are abandoned
- 😰 **No way to gauge maintainer responsiveness** — will your PR ever get reviewed?
- 🎲 **Random browsing** — GitHub search doesn't score repos on beginner-friendliness
- ⏰ **Wasted effort** — contributing to dead repos with no PR reviews
- 📊 **No metrics** — no visibility into PR merge rates, response times, or community health

## 💡 The Solution

OpenFirst fetches real-time data from the GitHub API, calculates custom **Activity** and **Beginner Friendliness** scores, and only surfaces repositories that are:

✅ **Actively maintained** (recent commits + merged PRs)  
✅ **Beginner-friendly** (good first issues, docs, responsive maintainers)  
✅ **Real, not abandoned** (validated with 6+ scoring factors per category)  
✅ **Continuously merging** (strict filter for repos with >50% PR merge rate)

---

## 📸 Features

### 🔎 Smart Explore Page
- Search & filter 200+ repositories by language, stars, and activity
- Sort by Activity Score, Beginner Friendliness, or Combined Score
- **"Active & Merging"** toggle — strict filter for only high-quality repos
- **Live GitHub Search** — if a repo isn't in our DB, we fetch it live from GitHub, score it, and display it

### 📊 Scoring Engine
Every repository gets two scores (0–100):

**Activity Score** — Is this repo alive?
| Factor | Weight | What it measures |
|---|---|---|
| Last commit recency | 25 pts | Days since last commit |
| PR merge velocity | 20 pts | Average time to merge PRs |
| Issue responsiveness | 15 pts | How fast maintainers respond |
| PR merge rate | 15 pts | Merged vs closed PRs |
| Community size | 15 pts | Contributors, stars, forks |
| Push recency | 10 pts | Days since last push |

**Beginner Friendliness Score** — Is this repo welcoming?
| Factor | Weight | What it measures |
|---|---|---|
| Good First Issues | 25 pts | Number of GFI-labeled issues |
| Documentation quality | 20 pts | README, CONTRIBUTING, CoC, templates |
| Maintainer responsiveness | 20 pts | Issue + PR response times |
| Community signals | 15 pts | Stars, contributor count |
| License friendliness | 10 pts | MIT, Apache, BSD = high score |
| Approachability | 10 pts | PR merge history |

### 📋 Issue Difficulty Estimator
Each "good first issue" is classified as **Easy**, **Medium**, or **Hard** using:
- Label analysis (e.g., "documentation" = easy, "security" = hard)
- Body length (short = easier, long = complex)
- Comment count (fewer comments = less discussion needed)

### 🔔 Subscription & Alert System
- Subscribe to **language + label** combinations (e.g., "Python + bug")
- Get notified when new repos match the "Active & Merging" criteria
- Get alerts when a saved repo **becomes inactive**

### ⚡ Active & Continuously Merging Filter
A repo qualifies only if ALL of these are true:
1. Commits within the last 30 days
2. Merged PRs within the last 30 days
3. PR merge rate > 50%
4. Not archived
5. More than 5 contributors

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                     │
│  Landing Page │ Explore Page │ Repo Detail │ Issues Page     │
│          http://localhost:3000                               │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API calls
┌──────────────────────▼──────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ API      │  │ Services     │  │ Background Jobs    │    │
│  │ Routes   │──│ • Repo Svc   │  │ • GitHub Sync      │    │
│  │ /v1/*    │  │ • Issue Svc  │  │ • Notification Svc │    │
│  │          │  │ • Scoring    │  │ • Inactivity Check │    │
│  └──────────┘  │ • GitHub API │  └───────┬────────────┘    │
│                └──────┬───────┘          │ APScheduler     │
│                       │                  │ (every 1 hour)  │
│  ┌────────────────────▼──────────────────▼──────────────┐  │
│  │              Data Layer                               │  │
│  │  PostgreSQL (repos, issues, subscriptions)            │  │
│  │  Redis (API response cache, 15-min TTL)               │  │
│  └───────────────────────────────────────────────────────┘  │
│          http://localhost:8000                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js 15 (App Router) | SSR, routing, UI |
| **Styling** | Tailwind CSS 4 | Dark glassmorphic theme |
| **Backend** | FastAPI + Uvicorn | Async REST API |
| **Database** | PostgreSQL 16 | Persistent storage |
| **Cache** | Redis 7 | API response caching |
| **ORM** | SQLAlchemy 2.0 (async) | Database queries |
| **Migrations** | Alembic | Schema versioning |
| **Scheduler** | APScheduler | Background sync jobs |
| **HTTP Client** | httpx | GitHub API calls |

---

## 📁 Project Structure

```
openfirst/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py              # Health check endpoint
│   │   │   └── v1/
│   │   │       ├── repositories.py    # Repo CRUD + live search
│   │   │       ├── issues.py          # Issue listing + filters
│   │   │       ├── stats.py           # Platform statistics
│   │   │       └── subscriptions.py   # Subscription CRUD + notifications
│   │   ├── core/
│   │   │   ├── cache.py               # Redis cache-aside service
│   │   │   ├── dependencies.py        # FastAPI dependency injection
│   │   │   └── exceptions.py          # Custom error classes
│   │   ├── models/
│   │   │   ├── repository.py          # Repository ORM model
│   │   │   ├── issue.py               # Issue ORM model
│   │   │   ├── language.py            # Language breakdown model
│   │   │   ├── metrics_history.py     # Historical score snapshots
│   │   │   ├── subscription.py        # User subscription model
│   │   │   └── notification.py        # Alert notification model
│   │   ├── services/
│   │   │   ├── github_client.py       # GitHub API wrapper (rate-limit aware)
│   │   │   ├── github_sync.py         # Background sync worker
│   │   │   ├── scoring_engine.py      # Activity + BF score calculators
│   │   │   ├── repository_service.py  # Repo query service with caching
│   │   │   ├── issue_service.py       # Issue query service
│   │   │   └── notification_service.py # Subscription alert processor
│   │   ├── tasks/
│   │   │   └── scheduler.py           # APScheduler job configuration
│   │   ├── config.py                  # Pydantic settings (env vars)
│   │   ├── database.py                # SQLAlchemy async engine
│   │   └── main.py                    # FastAPI app entry point
│   ├── alembic/                       # Database migrations
│   ├── requirements.txt
│   ├── seed.py                        # Manual sync trigger
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.js                # Landing page
│       │   ├── explore/page.js        # Explore + search + filters
│       │   ├── issues/page.js         # Global issue finder
│       │   └── repo/[id]/page.js      # Repo detail page
│       ├── components/
│       │   ├── Navbar.jsx             # Fixed navigation bar
│       │   ├── RepoCard.jsx           # Repository card component
│       │   └── ui/                    # Reusable UI components
│       └── lib/
│           ├── api.js                 # API client functions
│           └── utils.js               # Formatting helpers
├── docker-compose.yml                 # PostgreSQL + Redis + API
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 16+
- Redis 7+ (optional — app works without it)

### 1. Clone the Repo
```bash
git clone https://github.com/YOUR_USERNAME/openfirst.git
cd openfirst
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env → set DATABASE_URL, GITHUB_PAT
```

### 3. Database Setup
```bash
# Create the database
psql -U postgres -c "CREATE DATABASE openfirst;"

# Run migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head

# Seed initial data (fetches ~50 repos from GitHub)
python seed.py
```

### 4. Start Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- App: http://localhost:3000

---

## 🔑 Environment Variables

Create `backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/openfirst

# Redis (optional — works without it)
REDIS_URL=redis://localhost:6379/0

# GitHub Personal Access Token (required)
# Create at: https://github.com/settings/tokens → public_repo scope
GITHUB_PAT=ghp_xxxxxxxxxxxxxxxxxxxx

# App
APP_ENV=development
APP_DEBUG=true
CORS_ORIGINS=http://localhost:3000

# Sync Schedule
SYNC_INTERVAL_HOURS=1
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/repositories` | List repos with filters, sorting, pagination |
| `GET` | `/v1/repositories/live-search?q=` | Search GitHub live (fallback) |
| `GET` | `/v1/repositories/{id}` | Repo detail with scores, metrics, issues |
| `GET` | `/v1/repositories/{id}/issues` | Good first issues for a repo |
| `GET` | `/v1/repositories/{id}/metrics-history` | Historical score trends |
| `GET` | `/v1/issues` | Global issue finder with filters |
| `GET` | `/v1/stats` | Platform-wide statistics |
| `GET` | `/v1/languages` | Available languages with counts |
| `POST` | `/v1/subscriptions` | Create alert subscription |
| `GET` | `/v1/subscriptions?email=` | List user subscriptions |
| `DELETE` | `/v1/subscriptions/{id}` | Unsubscribe |
| `GET` | `/v1/subscriptions/notifications?email=` | Get alerts |
| `GET` | `/health` | Health check |

### Query Parameters for `/v1/repositories`

| Param | Type | Description |
|---|---|---|
| `search` | string | Search name and description |
| `language` | string | Filter by language (Python, JavaScript, etc.) |
| `sort_by` | string | `combined_score`, `activity_score`, `stars`, etc. |
| `has_issues` | bool | Must have open good-first-issues |
| `actively_merging` | bool | **Strict filter** — only actively merging repos |
| `min_stars` | int | Minimum star count |
| `page` / `per_page` | int | Pagination |

---

## 🌐 Deployment

### Docker Compose (recommended for local)
```bash
docker-compose up -d
```
Starts PostgreSQL, Redis, and the API.

### Azure / VPS Deployment
1. Install: Python, Node.js, PostgreSQL, Redis, Nginx
2. Clone repo to `/opt/openfirst`
3. Set up backend with Gunicorn:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
4. Build & serve frontend:
   ```bash
   cd frontend && npm run build && npm start
   ```
5. Configure Nginx as reverse proxy
6. Add SSL with Let's Encrypt

### Vercel + Render (free tier)
- **Frontend** → Vercel (auto-detected as Next.js)
- **Backend** → Render (set root dir to `backend`)
- **Database** → Neon (free 500MB PostgreSQL)
- **Redis** → Upstash (free 10K commands/day)

---

## ⚙️ How the Sync Works

```
Every 1 hour (configurable):
  1. 🔍 DISCOVER — search GitHub for repos with good-first-issues across 10 languages
  2. 📊 DEEP FETCH — for each repo: contributors, languages, PRs, issues, community profile
  3. 🧮 SCORE — calculate Activity (0-100) + Beginner Friendliness (0-100)
  4. 🏷️  CLASSIFY — estimate issue difficulty (easy/medium/hard)
  5. 💾 UPSERT — save or update repo + issues + languages in PostgreSQL
  6. 🚫 INACTIVITY — mark repos with 60+ days of no commits as inactive
  7. 🔔 NOTIFY — check subscriptions and generate alerts for new matches
```

**Rate limit handling:** Each sync uses ~1,200 API calls (well within the 5,000/hour PAT limit). If rate limit drops below 200, the sync auto-pauses for 30 seconds.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/cool-thing`
3. Commit changes: `git commit -m "Add cool thing"`
4. Push: `git push origin feature/cool-thing`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <b>Built with ❤️ to make open source accessible to everyone.</b>
</div>
