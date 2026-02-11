# app/models/quota.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class UserQuota(Base):
    __tablename__ = "user_quotas"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_quota_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # سهمیه ماهانه (ساعت GPU)
    monthly_quota_hours: Mapped[float] = mapped_column(Float, default=10.0)

    # میزان مصرف‌شده در این ماه
    used_hours_this_month: Mapped[float] = mapped_column(Float, default=0.0)

    # شروع دوره (مثلا اول ماه جاری - فعلا ساده: همون زمان ایجاد رکورد)
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    # اگر خواستیم بعداً reset کنیم می‌تونیم این فیلد رو آپدیت کنیم
    period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="quota")
