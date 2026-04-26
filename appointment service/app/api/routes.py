from fastapi import APIRouter, HTTPException, status

from app.schemas.appointments import (
    AppointmentCreateRequest,
    AppointmentCreateResponse,
    AppointmentRead,
    PatientAppointmentSummary,
)
from app.services.database_client import DatabaseServiceClient, DatabaseServiceError

router = APIRouter()
db_client = DatabaseServiceClient()


@router.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/appointments", response_model=list[AppointmentRead], tags=["appointments"])
def list_appointments() -> list[AppointmentRead]:
    try:
        return db_client.list_appointments()
    except DatabaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/appointments/patient/{patient_id}", response_model=list[AppointmentRead], tags=["appointments"])
def list_patient_appointments(patient_id: int) -> list[AppointmentRead]:
    try:
        patient = db_client.get_patient(patient_id)
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="patient not found")

        appointments = db_client.list_appointments()
        return [appointment for appointment in appointments if appointment.patient_id == patient_id]
    except DatabaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get(
    "/appointments/patient/{patient_id}/summary",
    response_model=PatientAppointmentSummary,
    tags=["appointments"],
)
def get_patient_summary(patient_id: int) -> PatientAppointmentSummary:
    try:
        patient = db_client.get_patient(patient_id)
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="patient not found")

        appointments = [item for item in db_client.list_appointments() if item.patient_id == patient_id]
        scheduled = [item for item in appointments if item.status == "scheduled"]
        cancelled = [item for item in appointments if item.status == "cancelled"]

        return PatientAppointmentSummary(
            patient_id=patient_id,
            total_appointments=len(appointments),
            scheduled_count=len(scheduled),
            cancelled_count=len(cancelled),
            active_appointments=scheduled,
        )
    except DatabaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post(
    "/appointments",
    response_model=AppointmentCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["appointments"],
)
def create_appointment(payload: AppointmentCreateRequest) -> AppointmentCreateResponse:
    try:
        patient = db_client.get_patient(payload.patient_id)
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="patient not found")

        slot = db_client.get_slot(payload.slot_id)
        if slot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="slot not found")
        if slot.is_reserved:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slot is already reserved")

        appointment = db_client.create_appointment(payload)
        return AppointmentCreateResponse(
            message="appointment created successfully",
            appointment=appointment,
        )
    except DatabaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.patch(
    "/appointments/{appointment_id}/cancel",
    response_model=AppointmentCreateResponse,
    tags=["appointments"],
)
def cancel_appointment(appointment_id: int) -> AppointmentCreateResponse:
    try:
        appointment = db_client.cancel_appointment(appointment_id)
        if appointment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="appointment not found")

        return AppointmentCreateResponse(
            message="appointment cancelled successfully",
            appointment=appointment,
        )
    except DatabaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

