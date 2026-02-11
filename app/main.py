# app/main.py - Fixed version with CORS
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.routes_health import router as health_router
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_jobs import router as jobs_router
from app.api.v1.routes_admin_jobs import router as admin_jobs_router
from app.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="GPU as a Service - Simulation Mode API",
    )

    # ✅ اضافه کردن CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # در پروداکشن این رو محدود کنید به دامنه‌های مشخص
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ✅ Mount static files (frontend)
    app.mount("/ui", StaticFiles(directory="frontend"), name="frontend")

    # ✅ شامل کردن روت‌ها با prefix یکسان
    app.include_router(health_router, prefix=settings.API_V1_PREFIX)
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(jobs_router, prefix=settings.API_V1_PREFIX)
    app.include_router(admin_jobs_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", tags=["Root"])
    def read_root():
        return {
            "message": "GPU as a Service API - Simulation Mode",
            "docs": "/docs",
            "frontend": "/ui/index.html"
        }

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()
        print("✅ Database initialized")
        print(f"📄 API Docs: http://localhost:8000/docs")
        print(f"🌐 Frontend: http://localhost:8000/ui/index.html")

    return app


app = create_app()
