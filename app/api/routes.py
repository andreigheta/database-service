from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import crud, schemas
from app.db.session import get_db

router = APIRouter()


@router.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/patients", response_model=list[schemas.PatientRead], tags=["patients"])
def list_patients(db: Session = Depends(get_db)) -> list[schemas.PatientRead]:
    return crud.list_patients(db)


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
def list_slots(db: Session = Depends(get_db)) -> list[schemas.AvailabilitySlotRead]:
    return crud.list_slots(db)


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
def list_appointments(db: Session = Depends(get_db)) -> list[schemas.AppointmentRead]:
    return crud.list_appointments(db)


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
