# Netflix MVP — Scope

## Stack

- **Runtime:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), asyncpg
- **Database:** PostgreSQL 16 via Docker Compose
- **Migrations:** Alembic (001_initial + 002_seed)
- **Infrastructure:** Multi-stage Docker, Docker Compose (app + Postgres)

## Functional Requirements

| FR | Description | Acceptance |
|----|-------------|------------|
| FR1 | Catalog homepage with continue-watching, trending, and per-genre rows | `test_fr1_catalog_homepage.py` |
| FR2 | Full-text search across titles, genres, and cast | `test_fr2_search.py` |
| FR3 | ABR video streaming with DASH manifest and mock segments | `test_fr3_abr_streaming.py` |
| FR4 | Playback resume via heartbeat, displayed on homepage | `test_fr4_playback_resume.py` |
| FR5 | Profile CRUD with account-scoped name uniqueness | `test_fr5_profile_management.py` |

## Out of Scope

- Real CDN delivery (Open Connect)
- DRM / license key exchange / offline downloads
- Recommendation ML / personalization
- A/B testing framework
- Multi-region deployment
- User authentication / OAuth
- Billing / subscription management
- Parental controls enforcement
- Video encoding pipeline

## Build Plan

1. Data model + Alembic migrations (staff)
2. FR1 — Catalog homepage (staff)
3. FR4 — Playback heartbeat + resume (staff)
4. FR3 — ABR streaming (staff)
5. **Scaffold project skeleton** (senior)
6. **FR5 — Profile CRUD + accounts** (senior)
7. **FR2 — Full-text search** (senior)
8. **Docker, Compose & Deploy** (senior)
9. **White-box tests** (senior)
10. **README + docs** (senior)
