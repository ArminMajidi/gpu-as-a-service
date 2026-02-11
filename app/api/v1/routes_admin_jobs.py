# app/api/v1/routes_admin_jobs.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status,BackgroundTasks
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_user
from app.db.session import get_db
from app.models.job import Job, JobStatus
from app.models.user import User
from app.schemas.job import JobRead
from app.services.job_runner import simulate_job_run

router = APIRouter(
    prefix="/admin/jobs",
    tags=["Admin Jobs"],
)


def _get_job_or_404(db: Session, job_id: int) -> Job:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


@router.get("", response_model=List[JobRead])
def list_all_jobs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
    status_filter: Optional[JobStatus] = None,
):
    """
    لیست همه Jobها برای ادمین.
    امکان فیلتر روی status: ?status_filter=PENDING
    """
    query = db.query(Job)

    if status_filter is not None:
        query = query.filter(Job.status == status_filter)

    jobs = query.order_by(Job.created_at.desc()).all()
    return jobs


@router.post("/{job_id}/approve", response_model=JobRead)
def approve_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
) -> JobRead:
    """
    تایید Job توسط ادمین و تغییر وضعیت به APPROVED.
    
    فقط Job هایی که در وضعیت PENDING هستند قابل تایید هستند.
    بعد از تایید، Job آماده شروع اجرا می‌شود.
    
    Args:
        job_id: شناسه Job مورد نظر
        db: نشست دیتابیس (تزریق خودکار)
        current_admin: ادمین احراز هویت شده (تزریق خودکار)
        
    Returns:
        Job: Job تایید شده با status=APPROVED
        
    Raises:
        HTTPException 404: اگر Job یافت نشود
        HTTPException 400: اگر Job در وضعیت غیر از PENDING باشد
        
    Example:
        >>> # POST /api/v1/admin/jobs/1/approve
    """
    job = _get_job_or_404(db, job_id)

    if job.status != JobStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve a job in status {job.status}",
        )

    job.status = JobStatus.APPROVED
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/reject", response_model=JobRead)
def reject_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
) -> JobRead:
    """
    رد کردن Job توسط ادمین و تغییر وضعیت به REJECTED.
    
    فقط Job هایی که در وضعیت PENDING هستند قابل رد هستند.
    Job های رد شده دیگر قابل اجرا نیستند.
    
    Args:
        job_id: شناسه Job مورد نظر
        db: نشست دیتابیس (تزریق خودکار)
        current_admin: ادمین احراز هویت شده (تزریق خودکار)
        
    Returns:
        Job: Job رد شده با status=REJECTED
        
    Raises:
        HTTPException 404: اگر Job یافت نشود
        HTTPException 400: اگر Job در وضعیت غیر از PENDING باشد
        
    Example:
        >>> # POST /api/v1/admin/jobs/1/reject
    """
    job = _get_job_or_404(db, job_id)

    if job.status != JobStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject a job in status {job.status}",
        )

    job.status = JobStatus.REJECTED
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/start", response_model=JobRead)
def start_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
) -> JobRead:
    """
    شروع اجرای Job در حالت شبیه‌سازی.
    
    فقط Job های تایید شده (APPROVED) قابل اجرا هستند.
    بعد از شروع، یک Background Task برای شبیه‌سازی اجرا ایجاد می‌شود.
    
    فرآیند:
    1. وضعیت به RUNNING تغییر می‌کند
    2. زمان شروع ثبت می‌شود
    3. یک task پس‌زمینه برای شبیه‌سازی اجرا می‌شود
    4. پس از اتمام، وضعیت به COMPLETED یا FAILED تغییر می‌کند
    
    Args:
        job_id: شناسه Job مورد نظر
        background_tasks: مدیریت taskهای پس‌زمینه (تزریق خودکار)
        db: نشست دیتابیس (تزریق خودکار)
        current_admin: ادمین احراز هویت شده (تزریق خودکار)
        
    Returns:
        Job: Job در حال اجرا با status=RUNNING
        
    Raises:
        HTTPException 404: اگر Job یافت نشود
        HTTPException 400: اگر Job در وضعیت غیر از APPROVED باشد
        
    Example:
        >>> # POST /api/v1/admin/jobs/1/start
        >>> # Job شروع به اجرا می‌کند در background
    """
    from datetime import datetime

    job = _get_job_or_404(db, job_id)

    if job.status != JobStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start a job in status {job.status}",
        )

    job.status = JobStatus.RUNNING
    job.started_at = datetime.utcnow()
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        simulate_job_run,
        job_id=job.id,
        estimated_hours=job.estimated_hours,
        num_gpus=job.num_gpus,
    )

    return job




@router.post("/{job_id}/complete", response_model=JobRead)
def complete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """
    علامت زدن Job به عنوان COMPLETED.
    فقط اگر status = RUNNING باشد.
    """
    from datetime import datetime

    job = _get_job_or_404(db, job_id)

    if job.status != JobStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete a job in status {job.status}",
        )

    job.status = JobStatus.COMPLETED
    job.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/fail", response_model=JobRead)
def fail_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """
    علامت زدن Job به عنوان FAILED.
    فقط اگر status = RUNNING باشد.
    یک پیام اختیاری خطا می‌تونیم بعداً اضافه کنیم.
    """
    from datetime import datetime

    job = _get_job_or_404(db, job_id)

    if job.status != JobStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot fail a job in status {job.status}",
        )

    job.status = JobStatus.FAILED
    job.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job
