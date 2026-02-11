<<<<<<< HEAD
# 🎛 GPU Job Simulation Service

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)

**یک سیستم کامل GPU as a Service با FastAPI، PostgreSQL و Docker**

[معماری](#-معماری-سیستم) • [نصب و اجرا](#-نصب-و-اجرا) • [مستندات API](#-مستندات-api) • [تست](#-تست) • [Demo](#-demo)

</div>

---

## 📋 فهرست

- [درباره پروژه](#-درباره-پروژه)
- [ویژگی‌ها](#-ویژگیها)
- [معماری سیستم](#-معماری-سیستم)
- [تکنولوژی‌ها](#-تکنولوژیها)
- [نصب و اجرا](#-نصب-و-اجرا)
- [مستندات API](#-مستندات-api)
- [تست](#-تست)
- [استفاده](#-استفاده)
- [ساختار پروژه](#-ساختار-پروژه)
- [مشارکت](#-مشارکت)

---

## 🚀 درباره پروژه

این پروژه یک سرویس **GPU as a Service** است که به کاربران اجازه می‌دهد Job های GPU خود را ثبت کنند و ادمین‌ها بتوانند آن‌ها را مدیریت کنند. سیستم در حالت **شبیه‌سازی** کار می‌کند و نیازی به GPU واقعی ندارد، اما تمام فرآیندهای واقعی را شبیه‌سازی می‌کند.

### 🎯 هدف

ارائه یک راه‌حل مدرن، ایمن و مقیاس‌پذیر برای مدیریت منابع GPU به صورت Multi-tenant با:
- مدیریت سهمیه (Quota Management)
- احراز هویت امن (JWT Authentication)
- چرخه کامل Job Lifecycle
- رابط کاربری ساده

---

## ✨ ویژگی‌ها

### 🔐 احراز هویت و امنیت
- ✅ احراز هویت کامل با **JWT Token**
- ✅ هش کردن رمز عبور با **bcrypt**
- ✅ تفکیک نقش **User / Admin**
- ✅ اعتبارسنجی ورودی با **Pydantic**

### 📊 مدیریت Job
- ✅ ثبت Job با مشخصات GPU (نوع، تعداد، ساعت)
- ✅ چرخه کامل: `PENDING → APPROVED → RUNNING → COMPLETED/FAILED`
- ✅ نیاز به تایید ادمین قبل از اجرا
- ✅ اجرای پس‌زمینه با **BackgroundTasks**
- ✅ شبیه‌سازی واقع‌گرایانه اجرا

### 💰 مدیریت سهمیه
- ✅ سهمیه ماهانه GPU برای هر کاربر
- ✅ بررسی خودکار سهمیه قبل از ثبت Job
- ✅ کم شدن خودکار از سهمیه
- ✅ ردیابی مصرف ماهانه

### 🗄️ دیتابیس
- ✅ استفاده از **PostgreSQL** (نه SQLite!)
- ✅ ORM با **SQLAlchemy**
- ✅ مدل‌های رابطه‌ای کامل
- ✅ آماده برای **Alembic Migrations**

### 🎨 رابط کاربری
- ✅ UI ساده با **Bootstrap 5**
- ✅ صفحات Login, Register, Dashboard, Admin Panel
- ✅ تعامل با API از طریق JavaScript

### 🧪 تست و کیفیت
- ✅ تست‌های خودکار با **pytest**
- ✅ Integration Tests
- ✅ CI/CD با **GitHub Actions**
- ✅ Type Hints و Docstrings

### 🐳 استقرار
- ✅ Dockerized کامل
- ✅ docker-compose برای راه‌اندازی آسان
- ✅ محیط development آماده

---

## 🏗 معماری سیستم

```
┌─────────────────────┐
│   کاربر/Frontend   │
│   (Bootstrap UI)    │
└──────────┬──────────┘
           │ HTTP Requests
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
│  ┌───────────────┐  │
│  │ Authentication│  │
│  │    (JWT)      │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │  API Routes   │  │
│  │  - User Jobs  │  │
│  │  - Admin Jobs │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │
      ┌────┴────┬──────────────┐
      ▼         ▼              ▼
┌──────────┐ ┌─────────┐ ┌──────────┐
│PostgreSQL│ │ Models  │ │  Worker  │
│ Database │ │  (ORM)  │ │ Runner   │
│          │ │ - User  │ │(Simulator)│
│          │ │ - Job   │ │          │
│          │ │ - Quota │ │          │
└──────────┘ └─────────┘ └──────────┘
```

برای جزئیات بیشتر: [ARCHITECTURE.md](./ARCHITECTURE.md)

### چرخه حیات Job

```
کاربر ثبت می‌کند
        ↓
    [PENDING] ──────→ ادمین رد می‌کند ──→ [REJECTED]
        ↓
ادمین تایید می‌کند
        ↓
    [APPROVED] ──────→ ادمین شروع می‌کند
        ↓
    [RUNNING]
        ↓
   ┌────┴────┐
   ▼         ▼
[COMPLETED] [FAILED]
```

---

## 🛠 تکنولوژی‌ها

| بخش | تکنولوژی | نسخه |
|-----|----------|------|
| Backend Framework | FastAPI | Latest |
| Language | Python | 3.11+ |
| Database | PostgreSQL | 16 |
| ORM | SQLAlchemy | 2.x |
| Authentication | PyJWT + Passlib | Latest |
| Password Hashing | bcrypt | 3.2.2 |
| Containerization | Docker + Compose | Latest |
| Testing | pytest | Latest |
| Frontend | Bootstrap 5 + Vanilla JS | 5.3 |
| CI/CD | GitHub Actions | - |

---

## 🚀 نصب و اجرا

### پیش‌نیازها

```bash
# Docker و Docker Compose باید نصب باشند
docker --version
docker-compose --version
```

### روش 1: اجرا با Docker (پیشنهادی)

```bash
# کلون کردن پروژه
git clone https://github.com/yourusername/gpu-task-manager-fastapi.git
cd gpu-task-manager-fastapi-main

# اجرای پروژه
docker-compose up --build

# منتظر این پیام‌ها بمانید:
# ✅ Database initialized
# 📄 API Docs: http://localhost:8000/docs
# 🌐 Frontend: http://localhost:8000/ui/index.html
```

**سرویس‌های در دسترس:**
- 📄 **Swagger UI**: http://localhost:8000/docs
- 🌐 **Frontend**: http://localhost:8000/ui/index.html
- 🗄️ **PostgreSQL**: localhost:5432

### روش 2: اجرای مستقیم (توسعه)

```bash
# ایجاد محیط مجازی
python -m venv venv
source venv/bin/activate  # در Windows: venv\Scripts\activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# تنظیم متغیرهای محیطی
export DB_USER=gpu_user
export DB_PASSWORD=gpu_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=gpu_service

# اجرای سرور
uvicorn app.main:app --reload
```

---

## 📚 مستندات API

### 🔐 Authentication

#### ثبت‌نام کاربر جدید
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "نام کاربر",
  "password": "123456"
}
```

**پاسخ:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "نام کاربر",
  "is_active": true,
  "is_admin": false
}
```

#### ورود و دریافت Token
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=123456
```

**پاسخ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### 👤 User Routes

#### ساخت Job جدید
```bash
POST /api/v1/jobs
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "ML Training Job",
  "gpu_type": "A100",
  "num_gpus": 2,
  "estimated_hours": 3,
  "command": "python train.py --epochs 100",
  "data_location": "/data/dataset",
  "is_sensitive": false
}
```

#### لیست Job های کاربر
```bash
GET /api/v1/jobs
Authorization: Bearer {token}

# با فیلتر:
GET /api/v1/jobs?status_filter=PENDING
```

#### جزئیات یک Job
```bash
GET /api/v1/jobs/{job_id}
Authorization: Bearer {token}
```

---

### 🛠 Admin Routes

#### تایید Job
```bash
POST /api/v1/admin/jobs/{job_id}/approve
Authorization: Bearer {admin_token}
```

#### رد Job
```bash
POST /api/v1/admin/jobs/{job_id}/reject
Authorization: Bearer {admin_token}
```

#### شروع اجرای Job
```bash
POST /api/v1/admin/jobs/{job_id}/start
Authorization: Bearer {admin_token}
```

#### لیست تمام Job ها
```bash
GET /api/v1/admin/jobs
Authorization: Bearer {admin_token}

# با فیلتر:
GET /api/v1/admin/jobs?status_filter=RUNNING
```

---

## 🧪 تست

### اجرای تست‌ها

```bash
# نصب pytest
pip install pytest pytest-cov httpx

# اجرای تمام تست‌ها
pytest tests/

# با نمایش جزئیات
pytest tests/ -v

# با Coverage Report
pytest --cov=app tests/ --cov-report=html

# فقط یک فایل خاص
pytest tests/test_auth_and_jobs.py
```

### Coverage Report

```bash
# تولید گزارش HTML
pytest --cov=app tests/ --cov-report=html

# باز کردن گزارش
open htmlcov/index.html
```

### تست‌های موجود

- ✅ `test_register_and_login`: تست ثبت‌نام و ورود
- ✅ `test_job_lifecycle_simulation`: تست کامل چرخه Job
- ✅ Integration Tests با SQLite
- ✅ Mock Database برای تست‌های سریع

---

## 💡 استفاده

### سناریو 1: کاربر عادی

```bash
# 1. ثبت‌نام
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.com",
    "password": "123456",
    "full_name": "Test User"
  }'

# 2. لاگین و دریافت Token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@test.com&password=123456" | jq -r '.access_token')

# 3. ساخت Job
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Job",
    "gpu_type": "A100",
    "num_gpus": 1,
    "estimated_hours": 2,
    "command": "python script.py"
  }'

# 4. مشاهده Job ها
curl -X GET http://localhost:8000/api/v1/jobs \
  -H "Authorization: Bearer $TOKEN"
```

### سناریو 2: ادمین

```bash
# 1. تبدیل کاربر به ادمین (در PostgreSQL)
docker exec -it gpu_db psql -U gpu_user -d gpu_service
UPDATE users SET is_admin = true WHERE email = 'user@test.com';

# 2. لاگین دوباره
ADMIN_TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@test.com&password=123456" | jq -r '.access_token')

# 3. تایید Job
curl -X POST http://localhost:8000/api/v1/admin/jobs/1/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 4. شروع Job
curl -X POST http://localhost:8000/api/v1/admin/jobs/1/start \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 5. مشاهده لاگ‌ها
docker logs -f gpu_api
```

---

## 📁 ساختار پروژه

```
gpu-task-manager-fastapi-main/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes_auth.py        # احراز هویت
│   │       ├── routes_jobs.py        # Job های کاربر
│   │       ├── routes_admin_jobs.py  # مدیریت ادمین
│   │       └── routes_health.py      # Health Check
│   ├── core/
│   │   ├── security.py               # JWT & Password
│   │   └── logging.py                # Logging Config
│   ├── db/
│   │   └── session.py                # Database Session
│   ├── models/
│   │   ├── user.py                   # User Model
│   │   ├── job.py                    # Job Model
│   │   └── quota.py                  # UserQuota Model
│   ├── schemas/
│   │   ├── user.py                   # User Schemas
│   │   ├── job.py                    # Job Schemas
│   │   └── auth.py                   # Auth Schemas
│   ├── services/
│   │   └── job_runner.py             # شبیه‌ساز Job
│   ├── config.py                     # تنظیمات
│   └── main.py                       # Entry Point
├── frontend/
│   ├── index.html                    # صفحه لاگین
│   ├── register.html                 # صفحه ثبت‌نام
│   ├── dashboard.html                # داشبورد کاربر
│   ├── admin.html                    # پنل ادمین
│   └── js/
│       ├── auth.js
│       ├── user.js
│       └── admin.js
├── tests/
│   └── test_auth_and_jobs.py         # تست‌های Integration
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions
├── docker-compose.yml                # Docker Compose
├── Dockerfile                        # Docker Image
├── requirements.txt                  # وابستگی‌ها
├── README.md                         # این فایل
├── ARCHITECTURE.md                   # معماری سیستم
├── CLASS_DIAGRAM.md                  # نمودار کلاس‌ها
└── DEMO_GUIDE.md                     # راهنمای Demo
```

---

## 🎬 Demo

برای راهنمای کامل Demo و ارائه، فایل [DEMO_GUIDE.md](./DEMO_GUIDE.md) را مطالعه کنید.

### Quick Demo

```bash
# 1. اجرای سیستم
docker-compose up

# 2. باز کردن Swagger UI
open http://localhost:8000/docs

# 3. یا استفاده از Frontend
open http://localhost:8000/ui/index.html
```

---

## 🔧 تنظیمات پیشرفته

### متغیرهای محیطی

یک فایل `.env` بسازید:

```env
# Database
DB_USER=gpu_user
DB_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432
DB_NAME=gpu_service

# JWT
JWT_SECRET_KEY=your_super_secret_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### استفاده از Alembic Migrations

```bash
# مقداردهی اولیه
alembic init migrations

# ایجاد migration
alembic revision --autogenerate -m "Initial migration"

# اعمال migrations
alembic upgrade head

# برگشت به نسخه قبل
alembic downgrade -1
```

---

## 🤝 مشارکت

این پروژه به عنوان تمرین درسی طراحی شده است. برای پیشنهادات یا اصلاحات:

1. Fork کنید
2. Branch جدید بسازید (`git checkout -b feature/AmazingFeature`)
3. Commit کنید (`git commit -m 'Add some AmazingFeature'`)
4. Push کنید (`git push origin feature/AmazingFeature`)
5. Pull Request باز کنید

---

## 📄 مجوز

این پروژه برای اهداف آموزشی ایجاد شده است.

---

## 👥 نویسندگان

- **تیم توسعه** - پروژه درس برنامه‌نویسی پیشرفته
- **استاد راهنما** - سیدامیرحسین طباطبایی

---

## 🙏 تشکر

- FastAPI به خاطر فریمورک عالی
- SQLAlchemy برای ORM قدرتمند
- PostgreSQL تیم برای دیتابیس قوی
- جامعه متن‌باز Python

---

## 📞 ارتباط

برای سوالات و پیشنهادات:
- 📧 Email: your.email@example.com
- 💬 GitHub Issues: [Issues](https://github.com/yourusername/gpu-task-manager-fastapi/issues)

---

<div align="center">

**ساخته شده با ❤️ و FastAPI**

[⬆ بازگشت به بالا](#-gpu-job-simulation-service)

</div>
=======
GPU as a Service 
>>>>>>> 49929342975201d85e3a46fabdc408ce3f17ee1c
