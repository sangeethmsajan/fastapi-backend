from fastapi import APIRouter
from app.api.routes import health, scan, dashboard

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(scan.router)
api_router.include_router(dashboard.router)