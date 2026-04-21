from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Appointment, AppointmentStatus, AvailabilitySlot, Patient
from app.db.schemas import AppointmentCreate, AvailabilitySlotCreate, PatientCreate


def list_patients(db: Session) -> list[Patient]:
    return list(db.scalars(select(Patient).order_by(Patient.created_at.desc())))


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


def list_slots(db: Session) -> list[AvailabilitySlot]:
    return list(db.scalars(select(AvailabilitySlot).order_by(AvailabilitySlot.start_time.asc())))


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


def list_appointments(db: Session) -> list[Appointment]:
    return list(db.scalars(select(Appointment).order_by(Appointment.created_at.desc())))


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
