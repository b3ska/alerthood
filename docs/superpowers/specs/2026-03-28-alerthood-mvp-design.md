# AlertHood MVP Design Spec

## Overview

Mobile-first web app for monitoring neighborhood threats. Users report events, the community votes on relevance/truthfulness, and severity is community-driven. Three main tabs: interactive map, Reddit-like feed, and user profile with gamification.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript |
| Map | MapLibre GL JS (open-source, no API key) |
| Backend API | FastAPI (Python) |
| Database / Auth / Realtime | Supabase (CLI-managed) |
| Storage | Supabase Storage (event photos) |
| Package Manager | pnpm |

## Architecture

Thin API + Supabase Direct pattern:

- **Reads:** Frontend reads via Supabase JS client, uses Realtime subscriptions for live updates
- **Writes:** All mutations go through FastAPI (business logic, karma calc, badge awards)
- **Auth:** Supabase Auth issues JWT -> frontend stores it -> sends to FastAPI in Authorization header -> FastAPI validates via Supabase JWT secret

```
Frontend (React+TS)
  ├── Supabase JS Client (reads + Realtime subscriptions)
  └── FastAPI Client (writes, JWT auth header)
        │
        ▼
FastAPI Backend
  - Create events, cast votes, manage areas
  - Auth middleware, badge/streak/karma logic
  - Photo upload to Supabase Storage
        │
        ▼
Supabase
  - Postgres DB + RLS policies
  - Auth (email/password + Google OAuth)
  - Realtime (websocket subscriptions)
  - Storage (event photos)
```

## MVP Scope

- User-generated reports only (no external API aggregation)
- Auth: email/password + Google OAuth
- Monitoring: radius around a point (lat/lng + meters), multiple areas per user
- Notifications: in-app only (banner/badge, no push)
- Threat categories: crime, infrastructure/utility, natural disaster, public disturbance
- Severity: community-driven via weighted votes (voter trust_score as weight)

## Data Model

Handled by a separate collaborator. Key entities: profiles, monitored_areas, events, votes, comments, badges, notifications.

## FastAPI Endpoints

### Auth
- `GET /auth/me` -> current user profile
- `PUT /auth/profile` -> update display_name, avatar

### Events
- `POST /events` -> create event (title, description, category, lat, lng, optional photo)
- `GET /events` -> list events (query: lat, lng, radius_m, category, sort=time|severity, page, limit)
- `GET /events/{id}` -> event detail + vote counts
- `POST /events/{id}/vote` -> cast vote (is_relevant, is_true)
- `PATCH /events/{id}/resolve` -> mark resolved (reporter only)

### Comments
- `POST /events/{id}/comments` -> add comment (body, optional parent_id for threads)
- `GET /events/{id}/comments` -> threaded comments for event

### Monitored Areas
- `POST /areas` -> create area (label, lat, lng, radius_m, notify_categories)
- `GET /areas` -> list user's areas
- `PUT /areas/{id}` -> update area
- `DELETE /areas/{id}` -> remove area

### Profile / Gamification
- `GET /profile` -> user profile + karma + trust_score + streak
- `GET /profile/badges` -> list earned badges
- `GET /profile/events` -> user's reported events

### Notifications
- `GET /notifications` -> list unread + recent (paginated)
- `PATCH /notifications/{id}` -> mark as read
- `PATCH /notifications/read-all` -> mark all as read

### Files
- `POST /upload/photo` -> upload event photo to Supabase Storage, return URL

## Frontend Component Structure

```
App
├── AuthProvider (Supabase auth context)
├── TabNav (bottom nav - Map | Feed | Profile)
│
├── MapTab
│   ├── MapView (MapLibre GL)
│   │   ├── EventMarker (icon per threat category)
│   │   └── MonitoredAreaCircle (radius overlay)
│   ├── EventPopup (on marker click - summary card)
│   ├── ReportEventModal (form + location picker + photo upload)
│   └── AreaManager (add/edit radius areas on map)
│
├── FeedTab
│   ├── FilterBar (category chips, area dropdown, sort toggle)
│   ├── PostList (infinite scroll)
│   │   └── PostCard (title, category badge, severity, time, relevance %)
│   ├── PostDetail
│   │   ├── PostHeader (full event info)
│   │   ├── VoteButtons (relevant/irrelevant, true/false)
│   │   └── CommentThread (recursive comments)
│   └── ReportEventButton (FAB, reuses ReportEventModal)
│
└── ProfileTab
    ├── ProfileHeader (avatar, name, karma, trust score)
    ├── StatBadges (streak counter, badge grid)
    ├── MonitoredAreasList (with edit/delete)
    └── NotificationPreferences (category toggles per area)

NotificationBanner (global - slides in from top, auto-dismisses)
```

## Realtime Subscriptions

- `events` table: filtered by user's monitored area bounding boxes - new events appear on map instantly
- `notifications` table: filtered for current user - triggers NotificationBanner
- `votes` table: filtered for events the user reported - live karma updates on profile
- Unsubscribe when switching away from relevant tab to save connections

## Severity Calculation

- Each event starts with severity_score = 0
- Each vote has weight = voter's trust_score (0.0 to 1.0)
- Upvote (relevant=true AND is_true=true) increases severity
- Downvote (relevant=false OR is_true=false) decreases severity
- severity_score = weighted sum of votes, normalized to 0-100
- New voters start with trust_score = 0.5, increases as their votes align with majority

## Mobile-First UI

- Bottom tab navigation (thumb-reachable)
- Map takes full viewport, controls overlay on top
- Feed uses card-based vertical scroll
- Touch-optimized: large tap targets for vote buttons, markers
- Single-column on mobile, map+feed side-by-side on desktop (stretch goal)

## Badge Types (MVP)

| Badge | Trigger |
|-------|---------|
| First Report | User creates first event |
| Trusted Reporter | trust_score >= 0.8 |
| Streak: 7 Days | 7 consecutive days with a relevant post |
| Streak: 30 Days | 30 consecutive days with a relevant post |
| 100 Upvotes | Cumulative upvotes on reported events >= 100 |
| Community Guardian | 50+ votes cast on others' events |

## Out of Scope (Post-MVP)

- Push notifications (device-level)
- External data sources (police feeds, news APIs)
- Custom area drawing on map
- Direct messaging between users
- Event photo gallery (multiple photos)
- Admin dashboard / moderation tools
