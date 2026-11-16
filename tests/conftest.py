"""Fixtures do pytest — banco SQLite isolado e cliente HTTP."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Env ANTES de importar a aplicação (engine/settings leem no import)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEST_DB = DATA_DIR / "test.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["ENV"] = "development"
os.environ["SECRET_KEY"] = "pytest-secret-key-nao-usar-em-producao"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.resolve().as_posix()}"
os.environ["SEED_ON_START"] = "true"
os.environ["ACCESS_TOKEN_MINUTES"] = "15"
os.environ["REFRESH_TOKEN_DAYS"] = "7"
os.environ["ALLOWED_ORIGINS"] = ""

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings

get_settings.cache_clear()

from app.deps import _login_hits  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """Sobe o app com lifespan (create_all + seed)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _limpar_rate_limit_login():
    """Evita 429 entre testes (mesmo IP + matrícula)."""
    _login_hits.clear()
    yield
    _login_hits.clear()


def login(client: TestClient, matricula: str = "A000001", senha: str = "demo1234") -> dict:
    r = client.post("/api/auth/login", json={"matricula": matricula, "senha": senha})
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture
def tokens_a1(client: TestClient) -> dict:
    return login(client, "A000001")


@pytest.fixture
def tokens_a2(client: TestClient) -> dict:
    return login(client, "A000002")


@pytest.fixture
def auth_a1(tokens_a1: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens_a1['access_token']}"}


@pytest.fixture
def auth_a2(tokens_a2: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens_a2['access_token']}"}
