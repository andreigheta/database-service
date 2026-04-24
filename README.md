# SmileSchedule Database Service

`database-service` is the persistence microservice for the SmileSchedule project. It exposes a small HTTP API that stores patients, availability slots and appointments in PostgreSQL, matching the project document requirements for:

- Python-based implementation
- PostgreSQL as the main database
- `pgAdmin` as the database management utility
- Docker / Docker Compose friendly local execution

## Current scope

This repository currently covers roughly the first half of the service:

- application bootstrap with FastAPI
- PostgreSQL connectivity through SQLAlchemy
- initial schema migration with Alembic
- CRUD endpoints for patients and availability slots
- appointment creation and cancellation flow
- filtered and paginated read endpoints for patients, slots and appointments
- individual record lookup endpoints for patients, slots and appointments
- local stack with PostgreSQL and `pgAdmin`

Remaining work can extend this foundation with authentication-aware access control, richer validation, automated tests and Swarm deployment descriptors.

## Project structure

```text
app/
  api/
  core/
  db/
alembic/
```

## Quick start

1. Copy `.env.example` to `.env`.
2. Start the stack:

```bash
docker compose up --build
```

3. Access the services:

- API docs: `http://localhost:8000/docs`
- `pgAdmin`: `http://localhost:5050`

## Example API usage

Create a patient:

```bash
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Maria Popescu",
    "email": "maria@example.com",
    "phone": "0712345678"
  }'
```

Create an availability slot:

```bash
curl -X POST http://localhost:8000/slots \
  -H "Content-Type: application/json" \
  -d '{
    "dentist_name": "Dr. Ionescu",
    "start_time": "2026-05-01T09:00:00Z",
    "end_time": "2026-05-01T09:30:00Z",
    "notes": "Consult initial"
  }'
```

Create an appointment:

```bash
curl -X POST http://localhost:8000/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "slot_id": 1,
    "reason": "Control periodic"
  }'
```

Filter appointments by patient and status:

```bash
curl "http://localhost:8000/appointments?patient_id=1&status=scheduled&limit=20"
```

Fetch a specific slot:

```bash
curl http://localhost:8000/slots/1
```

## Notes

- The service uses synchronous HTTP and a relational schema, which fits the SmileSchedule architecture described in the project PDF.
- `database-service` is intentionally focused on persistence concerns so it can be integrated later behind Kong together with the other SmileSchedule services.
