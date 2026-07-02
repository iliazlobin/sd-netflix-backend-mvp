# Netflix MVP — System Design

## Overview

A streaming backend for Netflix's core browsing and playback loop. One FastAPI process serves REST endpoints backed by PostgreSQL for catalog data, user profiles, playback state, search, and mock video segment delivery.

**Scale (MVP):** < 1,000 titles, < 100 profiles, single-digit QPS.

## Architecture

```
                  FastAPI App (port 8000)
                ┌──────────────────────────┐
                │  Routers (HTTP only)      │
                │  health · accounts · home │
                │  titles · streaming       │
                │  playback · profiles      │
                │  search                   │
                └──────────┬───────────────┘
                           │
                ┌──────────▼───────────────┐
                │  Services (business logic)│
                │  Account · Catalog · Title│
                │  Streaming · Playback    │
                │  Profile · Search        │
                └──────────┬───────────────┘
                           │
                ┌──────────▼───────────────┐
                │  PostgreSQL 16            │
                │  10 tables + GIN FTS     │
                │  indexes + constraints   │
                └──────────────────────────┘
```

## Data Model

10 tables: `accounts`, `profiles`, `titles`, `genres`, `title_genres`, `cast_members`, `title_cast`, `playback_progress`, `watch_history`, `video_segments`.

### Key Schema Decisions

- **PlaybackProgress** has `UNIQUE(profile_id, title_id)` — one row per profile+title pair. Heartbeat upserts via `INSERT ... ON CONFLICT DO UPDATE`.
- **WatchHistory** is append-only with 30-second debounce to prevent flooding on 5–10s heartbeat intervals.
- **trending_score** is a denormalized float on `titles` with a B-tree index.
- **FTS** uses three separate computed `tsvector` columns (titles, genres, cast_members), each with a GIN index. Search UNIONs across all three with `ts_rank` ordering and recency boost.
- **Profile.name** is unique per account via `UNIQUE(account_id, name)`.
- **VideoSegment.file_path** points to pre-generated mock .ts files (one file per quality level, shared across all titles).

## FRs Covered

| FR | Endpoint | Description |
|----|----------|-------------|
| — | `GET /healthz` | Liveness probe |
| — | `POST /api/v1/accounts` | Create account |
| — | `GET /api/v1/accounts/{id}` | Get account |
| FR1 | `GET /api/v1/home?profile_id=` | Catalog homepage (continue-watching, trending, genre rows) |
| — | `GET /api/v1/titles/{id}` | Title detail with cast and genres |
| FR3 | `GET /api/v1/titles/{id}/manifest` | DASH manifest XML |
| FR3 | `GET /api/v1/segments/{id}` | Raw video segment bytes |
| FR4 | `POST /api/v1/playback/heartbeat` | Upsert playback position |
| FR5 | `GET /api/v1/profiles?account_id=` | List profiles |
| FR5 | `POST /api/v1/profiles` | Create profile |
| FR5 | `PUT /api/v1/profiles/{id}` | Update profile |
| FR5 | `DELETE /api/v1/profiles/{id}` | Delete profile + cascade |
| FR2 | `GET /api/v1/search?q=&limit=` | Full-text search |

## Design Decisions

### D1: Postgres-only (no Redis)
At MVP scale (<1000 titles, <100 QPS), Postgres handles homepage queries in <10ms without caching. Redis would add operational complexity for zero latency benefit.

### D2: Debounced WatchHistory
Heartbeats fire every 5–10s. A 30-second cooldown on WatchHistory inserts reduces ~1000 rows per viewing session to ~180 — clean signal without table flooding.

### D3: Mock segments
One ~4KB .ts file per quality level; all segments of all titles reuse the same file. The player receives valid MPEG-TS bytes and can exercise ABR switching logic.

### D4: Account-scoped profile name uniqueness
`UNIQUE(account_id, name)` — two profiles on the same account can't share a name, but millions of accounts can each have a "Kids" profile.

### D5: Three separate FTS tsvector columns
Titles, genres, and cast_members each have their own GIN-indexed tsvector. Keeps data normalized (changing a cast member name doesn't cascade to titles) and allows per-source ranking.

### D6: No cursor pagination
The Netflix homepage is a fixed layout (~30 rows × ~12 titles). Search caps at 50 results. Neither needs cursor pagination at MVP scale.
