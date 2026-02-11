# app/models/job.py
from __future__ import annotations

from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"           # ثبت شده، منتظر بررسی ادمین
    APPROVED = "APPROVED"         # تایید شده، آماده اجرا
    REJECTED = "REJECTED"         # رد شده توسط ادمین
    RUNNING = "RUNNING"           # در حال اجرا
    COMPLETED = "COMPLETED"       # با موفقیت تمام شده
    FAILED = "FAILED"             # با خطا تمام شده


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # مالک Job
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # اطلاعات Job
    name: Mapped[str] = mapped_column(String(255))
    gpu_type: Mapped[str] = mapped_column(String(50))  # مثلا: "A100", "V100"
    num_gpus: Mapped[int] = mapped_column(Integer, default=1)
    estimated_hours: Mapped[float] = mapped_column(Float, default=1.0)

    command: Mapped[str] = mapped_column(Text)  # دستور اجرا (مثلا docker command / script)
    data_location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status_enum"),
        default=JobStatus.PENDING,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # رابطه با User
    user: Mapped["User"] = relationship(back_populates="jobs")
