from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import crud, schemas
from app.db.models import AppointmentStatus
from app.db.session import get_db

router = APIRouter()

PaginationLimit = Annotated[int, Query(ge=1, le=500)]
PaginationOffset = Annotated[int, Query(ge=0)]


@router.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/patients", response_model=list[schemas.PatientRead], tags=["patients"])
def list_patients(
    email: str | None = None,
    full_name: str | None = None,
    limit: PaginationLimit = 100,
    offset: PaginationOffset = 0,
    db: Session = Depends(get_db),
) -> list[schemas.PatientRead]:
    return crud.list_patients(db, email=email, full_name=full_name, limit=limit, offset=offset)


@router.get("/patients/{patient_id}", response_model=schemas.PatientRead, tags=["patients"])
def get_patient(patient_id: int, db: Session = Depends(get_db)) -> schemas.PatientRead:
    patient = crud.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="patient not found")

    return patient


@router.post(
    "/patients",
    response_model=schemas.PatientRead,
    status_code=status.HTTP_201_CREATED,
    tags=["patients"],
)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)) -> schemas.PatientRead:
    patient = crud.create_patient(db, payload)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="a patient with this email already exists",
        )

    return patient


@router.get("/slots", response_model=list[schemas.AvailabilitySlotRead], tags=["slots"])
def list_slots(
    dentist_name: str | None = None,
    start_from: datetime | None = None,
    start_to: datetime | None = None,
    is_reserved: bool | None = None,
    limit: PaginationLimit = 100,
    offset: PaginationOffset = 0,
    db: Session = Depends(get_db),
) -> list[schemas.AvailabilitySlotRead]:
    if start_from is not None and start_to is not None and start_to < start_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_to must be later than or equal to start_from",
        )

    return crud.list_slots(
        db,
        dentist_name=dentist_name,
        start_from=start_from,
        start_to=start_to,
        is_reserved=is_reserved,
        limit=limit,
        offset=offset,
    )


@router.get("/slots/{slot_id}", response_model=schemas.AvailabilitySlotRead, tags=["slots"])
def get_slot(slot_id: int, db: Session = Depends(get_db)) -> schemas.AvailabilitySlotRead:
    slot = crud.get_slot(db, slot_id)
    if slot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="slot not found")

    return slot


@router.post(
    "/slots",
    response_model=schemas.AvailabilitySlotRead,
    status_code=status.HTTP_201_CREATED,
    tags=["slots"],
)
def create_slot(
    payload: schemas.AvailabilitySlotCreate,
    db: Session = Depends(get_db),
) -> schemas.AvailabilitySlotRead:
    if payload.end_time <= payload.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be later than start_time",
        )

    slot = crud.create_slot(db, payload)
    if slot is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="slot overlaps an existing slot for this dentist",
        )

    return slot


@router.get("/appointments", response_model=list[schemas.AppointmentRead], tags=["appointments"])
def list_appointments(
    patient_id: int | None = None,
    slot_id: int | None = None,
    status_filter: AppointmentStatus | None = Query(default=None, alias="status"),
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    limit: PaginationLimit = 100,
    offset: PaginationOffset = 0,
    db: Session = Depends(get_db),
) -> list[schemas.AppointmentRead]:
    if created_from is not None and created_to is not None and created_to < created_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="created_to must be later than or equal to created_from",
        )

    return crud.list_appointments(
        db,
        patient_id=patient_id,
        slot_id=slot_id,
        status=status_filter,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
        offset=offset,
    )


@router.get("/appointments/{appointment_id}", response_model=schemas.AppointmentRead, tags=["appointments"])
def get_appointment(appointment_id: int, db: Session = Depends(get_db)) -> schemas.AppointmentRead:
    appointment = crud.get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="appointment not found")

    return appointment


@router.post(
    "/appointments",
    response_model=schemas.AppointmentRead,
    status_code=status.HTTP_201_CREATED,
    tags=["appointments"],
)
def create_appointment(
    payload: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
) -> schemas.AppointmentRead:
    appointment = crud.create_appointment(db, payload)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="slot is unavailable or patient does not exist",
        )

    return appointment


@router.patch(
    "/appointments/{appointment_id}/cancel",
    response_model=schemas.AppointmentRead,
    tags=["appointments"],
)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)) -> schemas.AppointmentRead:
    appointment = crud.cancel_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="appointment not found")

    return appointment
