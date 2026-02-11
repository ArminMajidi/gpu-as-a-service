# app/services/job_runner.py
from __future__ import annotations

import random
import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.job import Job, JobStatus
from app.core.logging import logger


def simulate_job_run(job_id: int, estimated_hours: float, num_gpus: int) -> None:
    """
    شبیه‌سازی اجرای Job در بک‌گراند.
    """
    try:
        logger.info(f"Job {job_id} started | GPUs={num_gpus} | hours={estimated_hours}")


        print(f"[JOB-RUNNER] Starting simulation for job_id={job_id} "
              f"(estimated_hours={estimated_hours}, num_gpus={num_gpus})",
              flush=True)

        simulated_seconds = int(estimated_hours * num_gpus)
        simulated_seconds = max(1, min(simulated_seconds, 10))

        print(f"[JOB-RUNNER] Sleeping for {simulated_seconds} seconds", flush=True)
        time.sleep(simulated_seconds)

        db: Session = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job is None:
                print(f"[JOB-RUNNER] Job {job_id} not found in DB", flush=True)
                return

            if job.status != JobStatus.RUNNING:
                print(f"[JOB-RUNNER] Job {job_id} status is {job.status}, "
                      f"not RUNNING. Skipping.", flush=True)
                return

            if random.random() < 0.8:
                job.status = JobStatus.COMPLETED
                logger.info(f"Job {job_id} completed successfully")

                job.error_message = None
                print(f"[JOB-RUNNER] Job {job_id} COMPLETED", flush=True)
            else:
                job.status = JobStatus.FAILED
                logger.error(f"Job {job_id} failed")
                job.error_message = "Simulated GPU failure"
                print(f"[JOB-RUNNER] Job {job_id} FAILED", flush=True)

            job.finished_at = datetime.utcnow()
            db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"[JOB-RUNNER] Exception in simulate_job_run(job_id={job_id}): {e}",
              flush=True)
