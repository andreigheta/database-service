# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

## [Unreleased]

### Added

- Initial `appointment-service` skeleton in a separate folder.
- FastAPI business-logic layer connected to the existing `database-service`.
- Appointment booking flow with patient and slot validation.
- Appointment cancellation flow delegated to `database-service`.
- Patient appointment listing and summary endpoints.
- Docker, environment template and project documentation for local execution.

