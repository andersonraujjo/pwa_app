"""Dependências FastAPI: autenticação e rate limit simples."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Aluno
from app.security import decodificar_access_token

bearer_scheme = HTTPBearer(auto_error=False)

# Limite: 5 tentativas / minuto por IP + matrícula (em memória; ok para demo)
_LOGIN_LIMIT = 5
_LOGIN_WINDOW = 60.0
_login_hits: dict[str, deque[float]] = defaultdict(deque)
_login_lock = Lock()


def checar_rate_limit_login(request: Request, matricula: str) -> None:
    """Bloqueia rajadas de login. Não registra a matrícula em log."""
    ip = request.client.host if request.client else "desconhecido"
    chave = f"{ip}|{matricula.strip().upper()}"
    agora = time.monotonic()
    with _login_lock:
        fila = _login_hits[chave]
        while fila and agora - fila[0] > _LOGIN_WINDOW:
            fila.popleft()
        if len(fila) >= _LOGIN_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas tentativas. Aguarde um momento e tente novamente.",
            )
        fila.append(agora)


def get_current_aluno(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Aluno:
    """Exige Bearer JWT e devolve o aluno do token (nunca confiar em id da URL)."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decodificar_access_token(credentials.credentials)
        aluno_id = int(payload["sub"])
    except (PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    aluno = db.scalar(
        select(Aluno)
        .options(joinedload(Aluno.curso))
        .where(Aluno.id == aluno_id)
    )
    if aluno is None or not aluno.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return aluno
