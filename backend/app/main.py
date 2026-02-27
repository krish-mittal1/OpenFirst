
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.dependencies import close_redis
from app.core.exceptions import OpenFirstError

logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting OpenFirst API v%s", settings.app_version)

    from app.tasks.scheduler import start_scheduler, stop_scheduler

    if settings.app_env != "testing":
        start_scheduler()

    yield

    logger.info("🛑 Shutting down OpenFirst API")
    if settings.app_env != "testing":
        stop_scheduler()
    await close_redis()

    from app.services.github_client import github_client
    await github_client.close()


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Helping beginners find and contribute to open source projects",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(OpenFirstError)
async def openfirst_error_handler(request: Request, exc: OpenFirstError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "status_code": exc.status_code},
    )


from app.api.health import router as health_router
from app.api.v1.repositories import router as repo_router
from app.api.v1.issues import router as issue_router
from app.api.v1.stats import router as stats_router
from app.api.v1.subscriptions import router as sub_router

app.include_router(health_router)
app.include_router(repo_router, prefix="/v1")
app.include_router(issue_router, prefix="/v1")
app.include_router(stats_router, prefix="/v1")
app.include_router(sub_router, prefix="/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "OpenFirst API",
        "version": settings.app_version,
        "docs": "/docs",
    }
