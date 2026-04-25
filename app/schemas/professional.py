from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import time

class WorkingHourBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time

class WorkingHourCreate(WorkingHourBase):
    pass

class WorkingHour(WorkingHourBase):
    id: int

    class Config:
        from_attributes = True

class ProfessionalBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    is_active: bool = True
    user_id: Optional[int] = None

class ProfessionalCreate(ProfessionalBase):
    pass

class ProfessionalUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    is_active: Optional[bool] = None
    user_id: Optional[int] = None

class Professional(ProfessionalBase):
    id: int
    working_hours: List[WorkingHour] = []

    class Config:
        from_attributes = True
