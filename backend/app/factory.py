from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.router import api_router
from backend.app.core.errors import AppError
from backend.app.schemas.common import ApiErrorDetail, ApiErrorResponse
from backend.config import settings


OPENAPI_TAGS = [
    {"name": "System", "description": "Service discovery and platform metadata."},
    {"name": "Models", "description": "Model registry and activation endpoints."},
    {"name": "Settings", "description": "Runtime business rules and platform settings."},
    {"name": "Inference", "description": "Single-image and batch inference APIs."},
    {"name": "Dashboard", "description": "High-level platform metrics and operations dashboard endpoints."},
    {"name": "Deployment", "description": "Deployment status, export and benchmark endpoints."},
    {"name": "History", "description": "Inference history and replay endpoints."},
    {"name": "Review", "description": "Manual review queue and bad case feedback endpoints."},
    {"name": "Retrain", "description": "Retrain sample catalog and sample lifecycle endpoints."},
    {"name": "Maintenance", "description": "Generated files and storage maintenance endpoints."},
    {"name": "Tasks", "description": "Async task submission and progress tracking endpoints."},
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="面向质检场景的多模型视觉检测与部署平台 API",
        version="2.0.0",
        description="支持模型管理、视觉检测、部署导出、性能评测与历史追踪的标准化 FastAPI 服务。",
        openapi_tags=OPENAPI_TAGS,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/artifacts", StaticFiles(directory=settings.artifacts_dir), name="artifacts")
    app.mount("/static", StaticFiles(directory=settings.project_root / "frontend"), name="static")

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        payload = ApiErrorResponse(
            message=exc.message,
            detail=exc.message,
            error=ApiErrorDetail(code=exc.code, message=exc.message, details=exc.details),
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        payload = ApiErrorResponse(
            message="请求参数校验失败。",
            detail="请求参数校验失败。",
            error=ApiErrorDetail(code="request_validation_error", message="请求参数校验失败。", details=exc.errors()),
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(HTTPException)
    async def handle_http_error(_: Request, exc: HTTPException) -> JSONResponse:
        message = str(exc.detail)
        payload = ApiErrorResponse(
            message=message,
            detail=message,
            error=ApiErrorDetail(code="http_error", message=message, details=None),
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        payload = ApiErrorResponse(
            message="服务器内部错误。",
            detail="服务器内部错误。",
            error=ApiErrorDetail(code="internal_server_error", message="服务器内部错误。", details={"reason": str(exc)}),
        )
        return JSONResponse(status_code=500, content=payload.model_dump())
