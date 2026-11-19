"""
FastAPI Main Application Entrypoint for News Event Detection and Tracking System.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.db.session import init_db
from backend.app.api.health import router as health_router
from backend.app.api.articles import router as articles_router
from backend.app.api.events import router as events_router
from backend.app.api.experiments import router as experiments_router
from backend.app.api.evaluation import router as evaluation_router
from backend.app.api.ingestion import router as ingestion_router
from backend.app.api.settings import router as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database schema safely
    init_db()
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title="News Event Detection and Tracking System",
    description="Time-Aware Semantic News Intelligence & Event Tracking API",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS for local development frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(articles_router, prefix=settings.API_V1_PREFIX)
app.include_router(events_router, prefix=settings.API_V1_PREFIX)
app.include_router(experiments_router, prefix=settings.API_V1_PREFIX)
app.include_router(evaluation_router, prefix=settings.API_V1_PREFIX)
app.include_router(ingestion_router, prefix=settings.API_V1_PREFIX)
app.include_router(settings_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "message": "Welcome to News Event Detection and Tracking System API",
        "docs_url": "/docs",
        "health_check": f"{settings.API_V1_PREFIX}/health",
        "metadata": f"{settings.API_V1_PREFIX}/metadata"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
