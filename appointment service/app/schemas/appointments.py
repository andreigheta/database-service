from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AppointmentStatus = Literal["scheduled", "cancelled"]


class AppointmentCreateRequest(BaseModel):
    patient_id: int
    slot_id: int
    reason: str = Field(min_length=3, max_length=255)


class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    slot_id: int
    reason: str
    status: AppointmentStatus
    created_at: datetime


class AppointmentCreateResponse(BaseModel):
    message: str
    appointment: AppointmentRead


class PatientAppointmentSummary(BaseModel):
    patient_id: int
    total_appointments: int
    scheduled_count: int
    cancelled_count: int
    active_appointments: list[AppointmentRead]


class PatientRead(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    created_at: datetime


class AvailabilitySlotRead(BaseModel):
    id: int
    dentist_name: str
    start_time: datetime
    end_time: datetime
    is_reserved: bool
    notes: str | None
    created_at: datetime

