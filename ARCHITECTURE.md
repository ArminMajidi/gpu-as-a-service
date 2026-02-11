# معماری سیستم GPU as a Service

## نمودار کلی سیستم

```mermaid
graph TB
    User[👤 کاربر / Frontend] -->|HTTP Request| API[🚀 FastAPI Backend]
    
    API -->|Authentication| JWT[🔐 JWT Token Validation]
    JWT -->|Verify| Auth{احراز هویت موفق؟}
    Auth -->|بله| Routes[API Routes]
    Auth -->|خیر| Error401[❌ 401 Unauthorized]
    
    Routes -->|User Routes| UserAPI["/api/v1/jobs"]
    Routes -->|Admin Routes| AdminAPI["/api/v1/admin/jobs"]
    
    UserAPI -->|CRUD| DB[(💾 PostgreSQL)]
    AdminAPI -->|CRUD| DB
    
    AdminAPI -->|Start Job| Worker[⚙️ Background Worker]
    Worker -->|Simulate| Simulator[🎮 Job Simulator]
    Simulator -->|Update Status| DB
    
    DB -->|Store| Models[📦 Models]
    Models -->|Contains| User[User Model]
    Models -->|Contains| Job[Job Model]
    Models -->|Contains| Quota[UserQuota Model]
    
    style API fill:#667eea
    style DB fill:#48bb78
    style Worker fill:#ed8936
    style User fill:#4299e1
```

## جزئیات لایه‌ها

### 1️⃣ Frontend Layer
- صفحات HTML با Bootstrap
- JavaScript برای ارتباط با API
- صفحات: Login, Register, Dashboard, Admin Panel

### 2️⃣ API Layer (FastAPI)
- **Authentication Routes** (`/api/v1/auth`):
  - POST `/register` - ثبت‌نام کاربر جدید
  - POST `/login` - ورود و دریافت JWT Token

- **User Job Routes** (`/api/v1/jobs`):
  - POST `/` - ایجاد Job جدید
  - GET `/` - لیست Job های کاربر
  - GET `/{id}` - جزئیات یک Job

- **Admin Routes** (`/api/v1/admin/jobs`):
  - POST `/{id}/approve` - تایید Job
  - POST `/{id}/reject` - رد Job
  - POST `/{id}/start` - شروع اجرای Job
  - POST `/{id}/complete` - علامت‌گذاری به عنوان تکمیل شده
  - POST `/{id}/fail` - علامت‌گذاری به عنوان شکست خورده

### 3️⃣ Database Layer
- **PostgreSQL** (نه SQLite!)
- جداول:
  - `users` - اطلاعات کاربران
  - `jobs` - Job های ثبت شده
  - `user_quotas` - سهمیه ماهانه کاربران

### 4️⃣ Background Worker
- استفاده از FastAPI BackgroundTasks
- شبیه‌سازی اجرای Job با time.sleep()
- آپدیت خودکار وضعیت Job

## چرخه حیات Job

```mermaid
stateDiagram-v2
    [*] --> PENDING: کاربر Job می‌سازد
    PENDING --> APPROVED: ادمین تایید می‌کند
    PENDING --> REJECTED: ادمین رد می‌کند
    APPROVED --> RUNNING: ادمین شروع می‌کند
    RUNNING --> COMPLETED: اجرای موفق (80%)
    RUNNING --> FAILED: اجرای ناموفق (20%)
    COMPLETED --> [*]
    FAILED --> [*]
    REJECTED --> [*]
```

## امنیت و احراز هویت

```mermaid
sequenceDiagram
    participant User as کاربر
    participant API as FastAPI
    participant DB as Database
    
    User->>API: POST /auth/login (email, password)
    API->>DB: Query User
    DB-->>API: User Data
    API->>API: verify_password()
    API->>API: create_access_token()
    API-->>User: JWT Token
    
    User->>API: Request با Bearer Token
    API->>API: Decode & Verify JWT
    API->>DB: Get User by ID
    DB-->>API: User Object
    API-->>User: Response
```

## بررسی سهمیه (Quota Check)

```mermaid
flowchart TD
    Start([کاربر Job جدید می‌سازد]) --> CheckQuota{سهمیه کافی؟}
    CheckQuota -->|بله| CreateJob[ایجاد Job با status=PENDING]
    CheckQuota -->|خیر| Error[❌ 400 Bad Request: سهمیه کافی نیست]
    CreateJob --> UpdateQuota[کم کردن از سهمیه]
    UpdateQuota --> SaveDB[(ذخیره در دیتابیس)]
    SaveDB --> Return([برگرداندن Job])
    Error --> Return
```

## استقرار (Deployment)

```mermaid
graph LR
    Docker[🐳 Docker Compose] --> DB_Container[Container: PostgreSQL]
    Docker --> API_Container[Container: FastAPI]
    
    API_Container --> Port8000[Port 8000]
    DB_Container --> Port5432[Port 5432]
    
    API_Container -.ENV.-> DB_Container
    
    style Docker fill:#2496ed
    style DB_Container fill:#336791
    style API_Container fill:#009485
```

---

## تکنولوژی‌های استفاده شده

| بخش | تکنولوژی | دلیل انتخاب |
|-----|----------|-------------|
| Backend Framework | FastAPI | سریع، مدرن، مستندسازی خودکار |
| Database | PostgreSQL | قدرتمند، production-ready |
| ORM | SQLAlchemy | استاندارد صنعت |
| Authentication | JWT + PyJWT | Stateless, امن |
| Password Hashing | Passlib + bcrypt | امنیت بالا |
| Containerization | Docker + Compose | استقرار آسان |
| Testing | Pytest | استاندارد Python |
| CI/CD | GitHub Actions | اتوماسیون تست |

---

## ویژگی‌های کلیدی

✅ **احراز هویت امن** با JWT  
✅ **تفکیک نقش** User/Admin  
✅ **مدیریت سهمیه** ماهانه GPU  
✅ **چرخه کامل Job** از ثبت تا اجرا  
✅ **شبیه‌سازی واقع‌گرایانه** بدون نیاز به GPU  
✅ **Background Processing** برای Job ها  
✅ **RESTful API** با مستندات Swagger  
✅ **Database Migration** با Alembic  
✅ **Frontend UI** ساده و کاربرپسند  
✅ **Automated Testing** با Coverage  
✅ **Docker Support** برای استقرار آسان  
