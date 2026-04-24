from pydantic import BaseModel, Field
from typing import Optional

class ServiceBase(BaseModel):
    name: str
    price: float = Field(ge=0, description="Price must be greater than or equal to zero")
    duration_minutes: int = Field(gt=0, description="Duration must be greater than zero")

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, gt=0)

class Service(ServiceBase):
    id: int

    class Config:
        from_attributes = True
