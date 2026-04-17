from sqlalchemy import String, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import enum
from .base import Base

class UserRole(enum.Enum):
    CLIENT = "client"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CLIENT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
