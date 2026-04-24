from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Appointment, AppointmentStatus, AvailabilitySlot, Patient
from app.db.schemas import AppointmentCreate, AvailabilitySlotCreate, PatientCreate


def list_patients(
    db: Session,
    *,
    email: str | None = None,
    full_name: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Patient]:
    query = select(Patient)

    if email is not None:
        query = query.where(Patient.email == email)
    if full_name is not None:
        query = query.where(Patient.full_name.ilike(f"%{full_name}%"))

    query = query.order_by(Patient.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query))


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.get(Patient, patient_id)


def create_patient(db: Session, payload: PatientCreate) -> Patient | None:
    patient = Patient(**payload.model_dump())
    db.add(patient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None

    db.refresh(patient)
    return patient


def list_slots(
    db: Session,
    *,
    dentist_name: str | None = None,
    start_from: datetime | None = None,
    start_to: datetime | None = None,
    is_reserved: bool | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AvailabilitySlot]:
    query = select(AvailabilitySlot)

    if dentist_name is not None:
        query = query.where(AvailabilitySlot.dentist_name.ilike(f"%{dentist_name}%"))
    if start_from is not None:
        query = query.where(AvailabilitySlot.start_time >= start_from)
    if start_to is not None:
        query = query.where(AvailabilitySlot.start_time <= start_to)
    if is_reserved is not None:
        query = query.where(AvailabilitySlot.is_reserved == is_reserved)

    query = query.order_by(AvailabilitySlot.start_time.asc()).offset(offset).limit(limit)
    return list(db.scalars(query))


def get_slot(db: Session, slot_id: int) -> AvailabilitySlot | None:
    return db.get(AvailabilitySlot, slot_id)


def create_slot(db: Session, payload: AvailabilitySlotCreate) -> AvailabilitySlot | None:
    overlapping_slot = db.scalar(
        select(AvailabilitySlot).where(
            and_(
                AvailabilitySlot.dentist_name == payload.dentist_name,
                or_(
                    and_(
                        AvailabilitySlot.start_time <= payload.start_time,
                        AvailabilitySlot.end_time > payload.start_time,
                    ),
                    and_(
                        AvailabilitySlot.start_time < payload.end_time,
                        AvailabilitySlot.end_time >= payload.end_time,
                    ),
                    and_(
                        AvailabilitySlot.start_time >= payload.start_time,
                        AvailabilitySlot.end_time <= payload.end_time,
                    ),
                ),
            )
        )
    )
    if overlapping_slot is not None:
        return None

    slot = AvailabilitySlot(**payload.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def list_appointments(
    db: Session,
    *,
    patient_id: int | None = None,
    slot_id: int | None = None,
    status: AppointmentStatus | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Appointment]:
    query = select(Appointment)

    if patient_id is not None:
        query = query.where(Appointment.patient_id == patient_id)
    if slot_id is not None:
        query = query.where(Appointment.slot_id == slot_id)
    if status is not None:
        query = query.where(Appointment.status == status)
    if created_from is not None:
        query = query.where(Appointment.created_at >= created_from)
    if created_to is not None:
        query = query.where(Appointment.created_at <= created_to)

    query = query.order_by(Appointment.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query))


def get_appointment(db: Session, appointment_id: int) -> Appointment | None:
    return db.get(Appointment, appointment_id)


def create_appointment(db: Session, payload: AppointmentCreate) -> Appointment | None:
    patient = db.get(Patient, payload.patient_id)
    slot = db.get(AvailabilitySlot, payload.slot_id)
    if patient is None or slot is None or slot.is_reserved:
        return None

    appointment = Appointment(**payload.model_dump())
    slot.is_reserved = True
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def cancel_appointment(db: Session, appointment_id: int) -> Appointment | None:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        return None

    appointment.status = AppointmentStatus.cancelled
    appointment.slot.is_reserved = False
    db.commit()
    db.refresh(appointment)
    return appointment
