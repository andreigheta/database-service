# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

### Added

- Database service lookup endpoints for individual patients, availability slots and appointments.
- Database service filtering support for patients by email or partial name.
- Database service filtering support for slots by dentist, reservation state and start-time window.
- Database service filtering support for appointments by patient, slot, status and creation window.
- Database service pagination controls (`limit` and `offset`) across list endpoints.

### Changed

- Bumped the `database-service` API version to `0.2.0`.
- Updated the project README examples to document filtered reads and direct record retrieval.

## [0.1.0]

### Added

- v1.1 Initial Python `FastAPI` service skeleton for the SmileSchedule database layer.
- v1.1 PostgreSQL integration via SQLAlchemy and `psycopg`.
- v1.1 Alembic configuration and first migration for patients, availability slots and appointments.
- v1.1 CRUD endpoints for patients and availability slots in `database-service`.
- v1.1 Appointment create and cancel persistence flows with slot reservation handling in `database-service`.
- v1.1 Separate `appointment service` folder implementing the SmileSchedule business-logic microservice.
- v1.1 HTTP integration layer from `appointment-service` to `database-service`.
- v1.1 Patient appointment listing, booking, cancellation and summary endpoints in `appointment-service`.
- v1.1 Dockerfile, Compose stack, `.env.example` and `pgAdmin` support for local database development.
- v1.1 Dockerfile, Compose stack and `.env.example` support for local appointment service development.
- v1.1 Project READMEs aligned with the SmileSchedule architecture from the project document.

### Changed

- Consolidated database and appointment service progress into a single root changelog in Keep a Changelog format.
