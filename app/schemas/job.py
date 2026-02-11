# app/schemas/job.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.job import JobStatus


class JobBase(BaseModel):
    name: str
    gpu_type: str
    num_gpus: int = 1
    estimated_hours: float = 1.0
    command: str
    data_location: Optional[str] = None
    is_sensitive: bool = False


class JobCreate(JobBase):
    pass


class JobRead(JobBase):
    id: int
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

    # Pydantic v2 – جایگزین orm_mode
    model_config = ConfigDict(from_attributes=True)
