# tests/test_auth_and_jobs.py
import time

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
import app.db.session as db_session
from app.db.session import Base, get_db
from app.models.user import User
import app.services.job_runner as job_runner

# -----------------------------
#  تنظیم دیتابیس تست (SQLite)
# -----------------------------

TEST_DATABASE_URL = "sqlite:///./test.db"

# یک engine جدید فقط برای تست
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# یک SessionLocal جدید که به sqlite متصل است
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

# جایگزین کردن engine و SessionLocal در ماژول اصلی db_session
db_session.engine = test_engine
db_session.SessionLocal = TestingSessionLocal

job_runner.SessionLocal = TestingSessionLocal

# ساخت اسکیمای دیتابیس تست
Base.metadata.drop_all(bind=test_engine)
Base.metadata.create_all(bind=test_engine)


# -----------------------------
#  override کردن dependency get_db
# -----------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def make_user_admin(email: str) -> None:
    """کمک‌کننده برای ادمین کردن یک کاربر در تست‌ها."""
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None, "User not found to promote to admin"
        user.is_admin = True
        db.commit()
    finally:
        db.close()


def test_register_and_login():
    email = "testuser@example.com"
    password = "123456"

    # ثبت‌نام
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": password,
        },
    )
    assert resp.status_code == 201, resp.text

    # لاگین
    resp = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_job_lifecycle_simulation():
    email = "jobuser@example.com"
    password = "123456"

    # ثبت‌نام کاربر
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Job User",
            "password": password,
        },
    )
    assert resp.status_code == 201, resp.text

    # ادمین کردن همین کاربر
    make_user_admin(email)

    # لاگین
    resp = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ساخت Job با مصرف کم quota
    resp = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "name": "Simulated Job CI",
            "gpu_type": "A100",
            "num_gpus": 1,
            "estimated_hours": 1,
            "command": "python train.py",
            "data_location": None,
        },
    )
    assert resp.status_code == 201, resp.text
    job = resp.json()
    job_id = job["id"]

    # ادمین → approve
    resp = client.post(
        f"/api/v1/admin/jobs/{job_id}/approve",
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "APPROVED"

    # ادمین → start (Simulation در بک‌گراند)
    resp = client.post(
        f"/api/v1/admin/jobs/{job_id}/start",
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "RUNNING"

    # صبر و polling تا Job از RUNNING خارج شود
    final_status = None
    for _ in range(10):
        resp = client.get(
            f"/api/v1/jobs/{job_id}",
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        if data["status"] != "RUNNING":
            final_status = data["status"]
            break
        time.sleep(1)  # یک ثانیه صبر بین هر چک

    assert final_status in ("COMPLETED", "FAILED"), f"Final status: {final_status}"
