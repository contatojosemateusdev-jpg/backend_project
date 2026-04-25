from sqlalchemy import String, Boolean, ForeignKey, Time, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .user import User

class Professional(Base):
    __tablename__ = "professionals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="professional_profile")
    working_hours: Mapped[list["ProfessionalWorkingHour"]] = relationship("ProfessionalWorkingHour", back_populates="professional", cascade="all, delete-orphan")

class ProfessionalWorkingHour(Base):
    __tablename__ = "professional_working_hours"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    professional_id: Mapped[int] = mapped_column(ForeignKey("professionals.id"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time: Mapped[float] = mapped_column(Time, nullable=False)  # Using Time for SQL
    end_time: Mapped[float] = mapped_column(Time, nullable=False)

    professional: Mapped["Professional"] = relationship("Professional", back_populates="working_hours")
