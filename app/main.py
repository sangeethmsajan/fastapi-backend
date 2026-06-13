from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.db.database import engine, Base
        import app.db.models
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        import logging
        logging.getLogger("uvicorn.error").warning(f"Database connection or table creation failed: {e}")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} is running"
    }