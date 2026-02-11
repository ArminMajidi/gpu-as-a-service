# app/api/v1/routes_health.py
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/ping")
def ping():
    return {"status": "ok"}
