from pydantic import BaseModel, Field
from typing import Optional

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

    class Config:
        from_attributes = True
