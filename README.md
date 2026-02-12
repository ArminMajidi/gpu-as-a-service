# GPU Task Manager

یه سرویس ساده برای مدیریت Job های GPU که با FastAPI نوشته شده.

## چیکار می‌کنه؟

کاربرا می‌تونن Job های GPU خودشون رو ثبت کنن، ادمین‌ها تایید می‌کنن و بعد اجرا میشه. همه چیز شبیه‌سازیه و نیازی به GPU واقعی نیست.

## تکنولوژی‌ها

- FastAPI برای Backend
- PostgreSQL برای Database
- Docker برای اجرا
- Bootstrap برای UI

## نصب

اگه Docker داری، خیلی راحته:

```bash
docker-compose up --build
```

بعد برو `http://localhost:8000/ui/index.html`

یا اگه می‌خوای مستقیم اجرا کنی:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

فقط یادت باشه PostgreSQL رو هم اجرا کنی و متغیرهای محیطی رو ست کنی.

## چطور کار می‌کنه؟

۱. کاربر ثبت‌نام می‌کنه و لاگین میشه
۲. Job جدید می‌سازه (نوع GPU، تعداد، ساعت و...)
۳. Job به حالت PENDING میره
۴. ادمین تایید یا رد می‌کنه
۵. اگه تایید شد، ادمین شروع می‌کنه
۶. Job اجرا میشه (شبیه‌سازی) و تمام میشه یا fail میشه

## API Docs

بعد از اجرا، برو `http://localhost:8000/docs` - اونجا همه endpoint ها رو می‌بینی و می‌تونی امتحان کنی.

## ویژگی‌های اصلی

- احراز هویت با JWT
- مدیریت سهمیه ماهانه برای هر کاربر
- پنل ادمین برای مدیریت Job ها
- UI ساده و کاربرپسند
- تست‌های خودکار

## تست

```bash
pytest tests/
```

## ساختار پروژه

```
app/
  ├── api/v1/          # route های API
  ├── models/          # مدل‌های دیتابیس
  ├── schemas/         # پایدنتیک schemas
  ├── services/        # لاجیک اصلی (مثل job runner)
  └── main.py          # entry point

frontend/            # فایل‌های HTML/JS/CSS
tests/              # تست‌ها
docker-compose.yml  # برای اجرا با Docker
```

## نکات

- تو حالت production حتماً `JWT_SECRET_KEY` رو عوض کن
- دیتابیس PostgreSQL استفاده میشه، نه SQLite
- برای تبدیل کاربر به ادمین باید مستقیم تو دیتابیس `is_admin` رو `true` کنی

## مجوز

پروژه آموزشیه، استفاده آزاد.
