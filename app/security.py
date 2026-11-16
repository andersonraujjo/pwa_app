"""Hash de senha (argon2) e JWT (access + refresh)."""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.config import get_settings

_ph = PasswordHasher()
ALGORITHM = "HS256"


def hash_senha(senha: str) -> str:
    return _ph.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return _ph.verify(senha_hash, senha)
    except VerifyMismatchError:
        return False


def _agora() -> datetime:
    return datetime.now(UTC)


def criar_access_token(*, aluno_id: int, matricula: str) -> str:
    settings = get_settings()
    exp = _agora() + timedelta(minutes=settings.access_token_minutes)
    payload = {
        "sub": str(aluno_id),
        "matricula": matricula,
        "type": "access",
        "exp": exp,
        "iat": _agora(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def criar_refresh_token_bruto() -> str:
    """Token opaco enviado ao cliente; só o hash fica no banco."""
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def refresh_expira_em() -> datetime:
    settings = get_settings()
    return _agora() + timedelta(days=settings.refresh_token_days)


def decodificar_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Tipo de token inválido")
    return payload


def criar_token_carteira(*, aluno_id: int, matricula: str, minutos: int = 5) -> str:
    """Token curto assinado embutido no QR da carteirinha."""
    settings = get_settings()
    exp = _agora() + timedelta(minutes=minutos)
    payload = {
        "sub": str(aluno_id),
        "matricula": matricula,
        "type": "carteira",
        "exp": exp,
        "iat": _agora(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
