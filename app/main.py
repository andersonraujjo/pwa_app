"""Aplicação FastAPI — API /api + front estático / PWA na raiz."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.routers import auth, me
from app.schemas import HealthOut
from app.seed import seed

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Cabeçalhos básicos de segurança + Cache-Control de SW/manifest."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "script-src 'self'; connect-src 'self'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
        )
        path = request.url.path
        if path in {"/sw.js", "/manifest.webmanifest"} or path.endswith(".webmanifest"):
            response.headers["Cache-Control"] = "no-cache"
        elif path.endswith((".js", ".css")):
            response.headers["Cache-Control"] = "no-cache"
        return response


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    init_db()
    if settings.seed_on_start:
        db = SessionLocal()
        try:
            seed(db)
        finally:
            db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="UniApp API",
        description="Portal do aluno — dados fictícios (projeto de extensão).",
        version="0.3.0",
        lifespan=lifespan,
    )

    origins = settings.cors_origins
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type"],
        )

    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/api/health", response_model=HealthOut, tags=["health"])
    def health() -> HealthOut:
        return HealthOut(status="ok", env=settings.env)

    app.include_router(auth.router, prefix="/api")
    app.include_router(me.router, prefix="/api")

    if STATIC_DIR.is_dir():
        app.mount("/css", StaticFiles(directory=STATIC_DIR / "css"), name="css")
        app.mount("/js", StaticFiles(directory=STATIC_DIR / "js"), name="js")
        icons_dir = STATIC_DIR / "icons"
        if icons_dir.is_dir():
            app.mount("/icons", StaticFiles(directory=icons_dir), name="icons")

        @app.get("/")
        def index() -> FileResponse:
            return FileResponse(STATIC_DIR / "index.html")

        @app.get("/sw.js")
        def service_worker() -> FileResponse:
            return FileResponse(
                STATIC_DIR / "sw.js",
                media_type="application/javascript; charset=utf-8",
                headers={"Cache-Control": "no-cache", "Service-Worker-Allowed": "/"},
            )

        @app.get("/manifest.webmanifest")
        def manifest() -> FileResponse:
            return FileResponse(
                STATIC_DIR / "manifest.webmanifest",
                media_type="application/manifest+json",
                headers={"Cache-Control": "no-cache"},
            )

        @app.get("/offline.html")
        def offline_page() -> FileResponse:
            return FileResponse(STATIC_DIR / "offline.html")

        @app.get("/{full_path:path}")
        def spa_fallback(full_path: str) -> Response:
            """Fallback SPA sem engolir /api nem /docs."""
            if full_path.startswith(("api/", "docs", "openapi.json", "redoc")):
                raise HTTPException(status_code=404)
            candidate = (STATIC_DIR / full_path).resolve()
            try:
                candidate.relative_to(STATIC_DIR.resolve())
            except ValueError as exc:
                raise HTTPException(status_code=404) from exc
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(STATIC_DIR / "index.html")

    return app


app = create_app()
