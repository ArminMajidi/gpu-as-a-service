# app/api/v1/routes_jobs.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.job import Job, JobStatus
from app.models.quota import UserQuota
from app.models.user import User
from app.schemas.job import JobCreate, JobRead

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


def _check_user_quota_or_raise(
    *,
    db: Session,
    user_id: int,
    requested_hours: float,
) -> None:
    """
    بررسی کفایت سهمیه GPU کاربر قبل از ساخت Job.
    
    این تابع سهمیه ماهانه کاربر را چک می‌کند و در صورت کافی نبودن،
    HTTPException رفع می‌کند.
    
    Args:
        db: نشست دیتابیس
        user_id: شناسه کاربر
        requested_hours: ساعت درخواستی (estimated_hours × num_gpus)
        
    Raises:
        HTTPException 500: اگر سهمیه کاربر یافت نشود (خطای سیستمی)
        HTTPException 400: اگر سهمیه کافی نباشد
        
    Example:
        >>> _check_user_quota_or_raise(db=db, user_id=1, requested_hours=6.0)
        >>> # اگر سهمیه کافی نباشد: HTTPException 400
    """
    quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
    if not quota:
        # نباید پیش بیاد؛ چون تو register براش quota ساختیم
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User quota not found",
        )

    available_hours = quota.monthly_quota_hours - quota.used_hours_this_month
    if requested_hours > available_hours:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Not enough GPU quota. "
                f"Requested: {requested_hours}h, "
                f"Available: {available_hours}h"
            ),
        )


@router.post(
    "",
    response_model=JobRead,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> JobRead:
    """
    ایجاد Job جدید برای کاربر با بررسی سهمیه.
    
    این endpoint:
    1. سهمیه کاربر را چک می‌کند (requested_hours = estimated_hours × num_gpus)
    2. در صورت کافی بودن، Job را با status=PENDING ایجاد می‌کند
    3. مقدار مصرف شده از سهمیه را افزایش می‌دهد
    
    Args:
        job_in: اطلاعات Job شامل نوع GPU، تعداد، ساعت تخمینی و دستور اجرا
        db: نشست دیتابیس (تزریق خودکار)
        current_user: کاربر احراز هویت شده (تزریق خودکار از JWT)
        
    Returns:
        Job: Job ایجاد شده با تمام اطلاعات
        
    Raises:
        HTTPException 400: اگر سهمیه کافی نباشد
        HTTPException 500: اگر سهمیه کاربر یافت نشود
        
    Example:
        >>> # POST /api/v1/jobs
        >>> {
        >>>   "name": "ML Training",
        >>>   "gpu_type": "A100",
        >>>   "num_gpus": 2,
        >>>   "estimated_hours": 3,
        >>>   "command": "python train.py"
        >>> }
    """
    requested_hours = job_in.estimated_hours * job_in.num_gpus
    _check_user_quota_or_raise(
        db=db,
        user_id=current_user.id,
        requested_hours=requested_hours,
    )

    db_job = Job(
        user_id=current_user.id,
        name=job_in.name,
        gpu_type=job_in.gpu_type,
        num_gpus=job_in.num_gpus,
        estimated_hours=job_in.estimated_hours,
        command=job_in.command,
        data_location=job_in.data_location,
        is_sensitive=job_in.is_sensitive,
        status=JobStatus.PENDING,
    )

    db.add(db_job)

    quota = db.query(UserQuota).filter(UserQuota.user_id == current_user.id).first()
    if quota is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User quota not found",
        )

    quota.used_hours_this_month += requested_hours

    db.commit()
    db.refresh(db_job)

    return db_job



@router.get("", response_model=List[JobRead])
def list_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    status_filter: Optional[JobStatus] = None,
) -> List[JobRead]:
    """
    دریافت لیست Job های کاربر لاگین‌شده.
    
    Args:
        db: نشست دیتابیس (تزریق خودکار)
        current_user: کاربر احراز هویت شده (تزریق خودکار)
        status_filter: فیلتر اختیاری برای وضعیت Job (مثلاً PENDING, RUNNING)
        
    Returns:
        لیست Job ها مرتب شده بر اساس تاریخ ایجاد (جدیدترین اول)
        
    Example:
        >>> # GET /api/v1/jobs
        >>> # GET /api/v1/jobs?status_filter=PENDING
    """
    query = db.query(Job).filter(Job.user_id == current_user.id)

    if status_filter is not None:
        query = query.filter(Job.status == status_filter)

    jobs = query.order_by(Job.created_at.desc()).all()
    return jobs


@router.get("/{job_id}", response_model=JobRead)
def get_job_detail(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> JobRead:
    """
    دریافت جزئیات کامل یک Job مشخص.
    
    کاربران عادی فقط می‌توانند Job های خود را مشاهده کنند.
    تلاش برای دسترسی به Job دیگران منجر به خطای 403 می‌شود.
    
    Args:
        job_id: شناسه Job مورد نظر
        db: نشست دیتابیس (تزریق خودکار)
        current_user: کاربر احراز هویت شده (تزریق خودکار)
        
    Returns:
        Job: اطلاعات کامل Job شامل وضعیت، زمان‌ها و خطاها
        
    Raises:
        HTTPException 404: اگر Job یافت نشود
        HTTPException 403: اگر Job متعلق به کاربر دیگری باشد
        
    Example:
        >>> # GET /api/v1/jobs/1
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this job",
        )

    return job
