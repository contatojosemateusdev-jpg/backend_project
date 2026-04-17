from sqlalchemy import ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from .base import Base

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    professional_id: Mapped[int] = mapped_column(ForeignKey("professionals.id"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)

    client: relationship("User")
    professional: relationship("Professional")
    service: relationship("Service")
