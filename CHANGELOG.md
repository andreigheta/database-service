# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial Python `FastAPI` service skeleton for the SmileSchedule database layer.
- PostgreSQL integration via SQLAlchemy and `psycopg`.
- Alembic configuration and first migration for patients, availability slots and appointments.
- CRUD endpoints for patients and availability slots.
- Appointment create and cancel flows with slot reservation handling.
- Dockerfile, Compose stack, `.env.example` and `pgAdmin` support for local development.
- Project README aligned with the SmileSchedule architecture from the project document.

