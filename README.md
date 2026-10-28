# GPS Attendance System

> [!NOTE]
> WORKING IN PROGRESS
>

This repository provides a FastAPI backend for a GPS-based classroom attendance system. Teachers can open attendance sessions for a class, students can check in from a configured geofence, and the system generates per-session and per-section attendance reports.

## What this API does

- User authentication with JWT bearer tokens
- Role-based access: ADMIN, TEACHER, STUDENT
- Account creation and listing, with admin-only creation/deletion
- Class section creation with teacher and student enrollment
- Attendance session creation using GPS center + radius + time window
- Student check-in validation using Haversine distance calculation
- Attendance reports for a session and for a section
- Token revocation support for logout

## Tech stack

- Python 3
- FastAPI
- SQLAlchemy + PostgreSQL
- Pydantic validation
- JWT authentication
- Docker Compose for PostgreSQL

## Quick start

1. Install Docker Desktop and make sure it is running.
2. Copy and rename `.env.example` to `.env`
3. Start PostgreSQL:

```bash
docker compose up -d --wait postgres
```

4. Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

5. Start the API:

```bash
uvicorn main:app --reload
```

The app is available at:

- OpenAPI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health root: http://127.0.0.1:8000/

## Environment variables

The project reads settings from `.env`:

```env
DATABASE_URL=postgresql+psycopg://attendance:attendance@localhost:5432/gps_attendance
JWT_SECRET=replace-with-a-long-random-secret
BOOTSTRAP_ADMIN_PASSWORD=replace-with-a-strong-password
```

If `BOOTSTRAP_ADMIN_PASSWORD` is set, the API creates an initial admin account with username `admin` on startup.

## Authentication

Use JWT bearer tokens returned by `/api/auth/login`.

```http
Authorization: Bearer <access_token>
```

Token expires after 30 minutes or when user log out manually.

## Main endpoints

| Area | Endpoint | Purpose |
|---|---|---|
| Auth | `POST /api/auth/login` | Log in and receive a JWT token |
| Auth | `POST /api/auth/logout` | Revoke the current token |
| Users | `POST /api/users` | Create an account (admin only) |
| Users | `GET /api/users` | List users with role/search pagination filters |
| Users | `DELETE /api/users/{id}` | Delete an account (admin only) |
| Sections | `POST /api/sections` | Create a class section with teachers and students |
| Sessions | `POST /api/sessions` | Open an attendance session |
| Sessions | `POST /api/sessions/{id}/check-in` | Validate student GPS check-in |
| Reports | `GET /api/reports/sessions/{id}` | Get report for one session |
| Reports | `GET /api/reports/sections/{id}` | Get cumulative report for one section |

## Attendance rules

- A session defines a geofence using a center coordinate, radius in meters, and a time window.
- A student check-in is evaluated with the Haversine formula.
- Status values:
  - `PRESENT` when the device is inside the radius
  - `REJECTED_OUT_OF_RANGE` when outside the radius
  - `ABSENT` / `EXCUSED` are used in report aggregation logic
- Only users enrolled in the section can check in for that session.
- Only TEACHER and ADMIN roles can open a session or view attendance reports.

## Typical flow

1. Admin creates accounts for staff and students.
2. Admin creates a class section and assigns teachers/students.
3. Teacher logs in and opens an attendance session with a class geofence.
4. Student logs in and posts GPS coordinates to `/api/sessions/{id}/check-in`.
5. Teacher retrieves `/api/reports/sessions/{id}` or `/api/reports/sections/{id}`.
