from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.models import AppointmentStatus


class PatientCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=6, max_length=30)


class PatientRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AvailabilitySlotCreate(BaseModel):
    dentist_name: str = Field(min_length=3, max_length=120)
    start_time: datetime
    end_time: datetime
    notes: str | None = Field(default=None, max_length=1000)


class AvailabilitySlotRead(BaseModel):
    id: int
    dentist_name: str
    start_time: datetime
    end_time: datetime
    is_reserved: bool
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)

