from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from championships.u_cup_2024.router import router as u_cup_2024_router
from core.settings import settings


app = FastAPI(title=settings.PROJECT_NAME, description=settings.DESCRIPTION)


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(u_cup_2024_router, prefix="/u_cup_2024", tags=["U Cup 2024"])
