from contextlib import asynccontextmanager
from typing import Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config.settings import settings
from src.core.exceptions import AppError
from src.frontend import SPAStaticFiles
from src.database.init_db import create_tables, seed_demo_data
from src.database.session import SessionLocal
from src.routers import auth, favorites, health, products, transactions, users, uploads, forum, activity


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.auto_create_tables:
        create_tables()
    if settings.seed_demo_data:
        with SessionLocal() as db:
            seed_demo_data(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="福帮帮校园二手资源流转平台 Phase 1 REST API",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def error_response(status_code: int, message: str, data: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": status_code, "message": message, "data": data},
    )


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return error_response(exc.status_code, exc.message, exc.data)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "请求失败"
    return error_response(exc.status_code, message)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {
            "field": ".".join(str(part) for part in item["loc"] if part != "body"),
            "message": item["msg"],
        }
        for item in exc.errors()
    ]
    return error_response(422, "请求参数校验失败", errors)


app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(favorites.router, prefix=settings.api_prefix)
app.include_router(transactions.router, prefix=settings.api_prefix)
app.include_router(uploads.router, prefix=settings.api_prefix)
app.include_router(forum.router, prefix=settings.api_prefix)
app.include_router(activity.router, prefix=settings.api_prefix)


@app.get("/", include_in_schema=False, response_model=None)
def root():
    if settings.frontend_dist:
        return FileResponse(Path(settings.frontend_dist) / 'index.html')
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
    }


if settings.frontend_dist:
    app.mount('/', SPAStaticFiles(directory=settings.frontend_dist, html=True), name='frontend')

