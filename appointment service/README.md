# SmileSchedule Appointment Service

`appointment-service` is the business-logic microservice for SmileSchedule. It sits in front of `database-service` and coordinates the appointment flow used by patients and administrators.

## Current scope

This implementation covers roughly half of the service:

- FastAPI application bootstrap
- HTTP integration with `database-service`
- patient lookup before booking
- slot availability checks before booking
- appointment creation and cancellation through the persistence service
- patient-oriented listing and summary endpoints
- container-ready local setup

The remaining half can add auth integration, retries/circuit breaking, async messaging, tests, admin workflows and Swarm/Kong descriptors.

## Service role in the project

According to the project document, SmileSchedule should contain:

- an authentication service
- a business-logic service
- a database-facing service

This repository folder implements the business-logic layer. It does not store data directly. Instead, it communicates synchronously over HTTP with the existing `database-service`.

## Environment

Copy `.env.example` to `.env` and adjust values if needed.

Important variable:

- `DATABASE_SERVICE_URL`: base URL of the existing `database-service`

## Run locally

```bash
docker compose up --build
```

Swagger UI will be available at `http://localhost:8100/docs`.

## Main endpoints

- `GET /health`
- `GET /appointments`
- `GET /appointments/patient/{patient_id}`
- `GET /appointments/patient/{patient_id}/summary`
- `POST /appointments`
- `PATCH /appointments/{appointment_id}/cancel`

## Integration note

To book an appointment successfully, the target `database-service` must already expose:

- `GET /patients`
- `GET /slots`
- `GET /appointments`
- `POST /appointments`
- `PATCH /appointments/{id}/cancel`

