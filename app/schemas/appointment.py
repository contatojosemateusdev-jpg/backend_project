from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AppointmentBase(BaseModel):
    professional_id: int
    service_id: int
    start_time: datetime

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    start_time: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None

class Appointment(AppointmentBase):
    id: int
    client_id: int
    end_time: datetime
    status: AppointmentStatus

    class Config:
        from_attributes = True
