from collections.abc import Sequence

import httpx

from app.core.config import settings
from app.schemas.appointments import (
    AppointmentCreateRequest,
    AppointmentRead,
    AvailabilitySlotRead,
    PatientRead,
)


class DatabaseServiceError(Exception):
    pass


class DatabaseServiceClient:
    def __init__(self) -> None:
        self.base_url = settings.database_service_url.rstrip("/")
        self.timeout = settings.request_timeout_seconds

    def _request(self, method: str, path: str, json: dict | None = None) -> httpx.Response:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.request(method=method, url=url, json=json, timeout=self.timeout)
        except httpx.HTTPError as exc:
            raise DatabaseServiceError("database-service is unreachable") from exc

        if response.status_code >= 500:
            raise DatabaseServiceError("database-service returned a server error")

        return response

    def list_patients(self) -> list[PatientRead]:
        response = self._request("GET", "/patients")
        response.raise_for_status()
        return [PatientRead.model_validate(item) for item in response.json()]

    def get_patient(self, patient_id: int) -> PatientRead | None:
        patients = self.list_patients()
        return next((patient for patient in patients if patient.id == patient_id), None)

    def list_slots(self) -> list[AvailabilitySlotRead]:
        response = self._request("GET", "/slots")
        response.raise_for_status()
        return [AvailabilitySlotRead.model_validate(item) for item in response.json()]

    def get_slot(self, slot_id: int) -> AvailabilitySlotRead | None:
        slots = self.list_slots()
        return next((slot for slot in slots if slot.id == slot_id), None)

    def list_appointments(self) -> list[AppointmentRead]:
        response = self._request("GET", "/appointments")
        response.raise_for_status()
        return [AppointmentRead.model_validate(item) for item in response.json()]

    def create_appointment(self, payload: AppointmentCreateRequest) -> AppointmentRead:
        response = self._request("POST", "/appointments", json=payload.model_dump(mode="json"))
        if response.status_code == 409:
            raise DatabaseServiceError("database-service rejected the appointment request")

        response.raise_for_status()
        return AppointmentRead.model_validate(response.json())

    def cancel_appointment(self, appointment_id: int) -> AppointmentRead | None:
        appointments: Sequence[AppointmentRead] = self.list_appointments()
        if not any(item.id == appointment_id for item in appointments):
            return None

        response = self._request("PATCH", f"/appointments/{appointment_id}/cancel")
        response.raise_for_status()
        return AppointmentRead.model_validate(response.json())

