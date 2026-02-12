# GPU Task Manager

سیستم مدیریت Job های GPU با معماری RESTful API

## توضیحات پروژه

این پروژه یک سرویس GPU as a Service است که امکان ثبت، مدیریت و اجرای شبیه‌سازی شده Job های GPU را فراهم می‌کند. سیستم شامل احراز هویت کاربران، مدیریت سهمیه منابع و پنل مدیریتی برای ادمین‌ها است.

### ویژگی‌های اصلی

- **احراز هویت امن**: استفاده از JWT Token و هش کردن رمز عبور با bcrypt
- **مدیریت Job**: چرخه کامل از ثبت تا اجرا و نتیجه‌گیری
- **مدیریت سهمیه**: کنترل مصرف ماهانه GPU برای هر کاربر
- **پنل مدیریت**: رابط کاربری برای ادمین‌ها جهت تایید و راه‌اندازی Job ها
- **رابط کاربری**: داشبورد کاربرپسند برای مشاهده و ثبت Job ها

## تکنولوژی‌های استفاده شده

**Backend:**
- FastAPI - فریمورک وب
- SQLAlchemy - ORM
- PostgreSQL - دیتابیس
- PyJWT - احراز هویت
- Pydantic - اعتبارسنجی داده

**Frontend:**
- HTML/CSS/JavaScript
- Bootstrap 5

**DevOps:**
- Docker & Docker Compose
- pytest - تست خودکار

## نصب و راه‌اندازی

### با استفاده از Docker Compose

```bash
docker-compose up --build
```

سرویس بر روی پورت 8000 در دسترس خواهد بود.

### اجرای مستقیم

```bash
# ایجاد محیط مجازی
python -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای سرور
uvicorn app.main:app --reload
```

## دسترسی به سرویس‌ها

- **رابط کاربری**: `http://localhost:8000/ui/index.html`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## معماری سیستم

### مدل‌های دیتابیس

- **User**: اطلاعات کاربران و نقش آن‌ها
- **Job**: اطلاعات Job ها شامل وضعیت، نوع GPU و پارامترهای اجرا
- **UserQuota**: سهمیه ماهانه و مصرف هر کاربر

### چرخه حیات Job

```
PENDING → APPROVED → RUNNING → COMPLETED/FAILED
   ↓
REJECTED
```

1. کاربر Job را ثبت می‌کند (وضعیت: PENDING)
2. ادمین Job را بررسی و تایید یا رد می‌کند
3. در صورت تایید، ادمین Job را شروع می‌کند (وضعیت: RUNNING)
4. Job اجرا می‌شود و به وضعیت COMPLETED یا FAILED می‌رسد

### API Endpoints

**احراز هویت:**
- `POST /api/v1/auth/register` - ثبت‌نام کاربر جدید
- `POST /api/v1/auth/login` - ورود و دریافت توکن

**کاربر:**
- `GET /api/v1/jobs` - لیست Job های کاربر
- `POST /api/v1/jobs` - ثبت Job جدید
- `GET /api/v1/jobs/{id}` - جزئیات یک Job

**ادمین:**
- `GET /api/v1/admin/jobs` - لیست تمام Job ها
- `POST /api/v1/admin/jobs/{id}/approve` - تایید Job
- `POST /api/v1/admin/jobs/{id}/reject` - رد Job
- `POST /api/v1/admin/jobs/{id}/start` - شروع اجرای Job

## ساختار پروژه

```
gpu-task-manager-fastapi-main/
├── app/
│   ├── api/v1/              # API Routes
│   ├── models/              # Database Models
│   ├── schemas/             # Pydantic Schemas
│   ├── services/            # Business Logic
│   ├── core/                # Security & Config
│   ├── db/                  # Database Session
│   └── main.py              # Application Entry Point
├── frontend/                # UI Files
├── tests/                   # Test Suite
├── docker-compose.yml       # Docker Configuration
├── Dockerfile
├── requirements.txt
└── README.md
```

## تست

اجرای تست‌های خودکار:

```bash
pytest tests/
```

Coverage Report:

```bash
pytest --cov=app tests/
```

## امنیت

- استفاده از JWT برای احراز هویت
- هش کردن رمز عبور با الگوریتم bcrypt
- اعتبارسنجی ورودی‌ها با Pydantic
- تفکیک دسترسی کاربر و ادمین

## نکات مهم

- برای تبدیل یک کاربر به ادمین، باید مقدار `is_admin` در دیتابیس را به `true` تغییر دهید
- در محیط production حتماً `JWT_SECRET_KEY` را تغییر دهید
- سیستم به صورت شبیه‌سازی کار می‌کند و نیازی به GPU فیزیکی ندارد

## مستندات تکمیلی

- `ARCHITECTURE.md` - جزئیات معماری سیستم
- `CLASS_DIAGRAM.md` - نمودار کلاس‌ها و روابط

## اطلاعات پروژه

**اعضا گروه**:  آرمین مجیدی ، کیانا حسین پور ، هستی راه پی
**استاد راهنما**: دکتر امیرحسین طباطبایی  
**درس**: برنامه‌نویسی پیشرفته
