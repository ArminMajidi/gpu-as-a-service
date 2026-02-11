# app/models/user.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    # روابط
    jobs: Mapped[List["Job"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    quota: Mapped[Optional["UserQuota"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
