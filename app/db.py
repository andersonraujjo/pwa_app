"""Engine e sessão SQLAlchemy 2.0 (síncrono)."""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Base declarativa dos modelos."""


def _ensure_sqlite_dir(url: str) -> None:
    """Garante a pasta do arquivo SQLite antes de abrir a conexão."""
    if not url.startswith("sqlite:///"):
        return
    caminho = url.removeprefix("sqlite:///")
    if caminho in {":memory:", ""} or caminho.startswith("file:"):
        return
    Path(caminho).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


settings = get_settings()
_ensure_sqlite_dir(settings.database_url)

connect_args: dict = {}
if settings.database_url.startswith("sqlite"):
    # Necessário para FastAPI + SQLite em threads do uvicorn
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def _sqlite_pragma(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
    """Ativa foreign keys no SQLite."""
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """Dependência FastAPI: uma sessão por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Cria as tabelas se ainda não existirem."""
    from app import models  # noqa: F401 — registra metadados

    Base.metadata.create_all(bind=engine)
