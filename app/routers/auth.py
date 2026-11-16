"""Login, refresh (com rotação) e logout."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.deps import checar_rate_limit_login
from app.models import Aluno, RefreshToken
from app.schemas import LoginIn, LogoutIn, MessageOut, RefreshIn, TokenOut
from app.security import (
    criar_access_token,
    criar_refresh_token_bruto,
    hash_token,
    refresh_expira_em,
    verificar_senha,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _emitir_tokens(db: Session, aluno: Aluno) -> TokenOut:
    access = criar_access_token(aluno_id=aluno.id, matricula=aluno.matricula)
    refresh_bruto = criar_refresh_token_bruto()
    db.add(
        RefreshToken(
            aluno_id=aluno.id,
            token_hash=hash_token(refresh_bruto),
            expira_em=refresh_expira_em(),
            revogado=False,
        )
    )
    db.commit()
    settings = get_settings()
    return TokenOut(
        access_token=access,
        refresh_token=refresh_bruto,
        expires_in=settings.access_token_minutes * 60,
    )


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    checar_rate_limit_login(request, payload.matricula)

    # Mensagem genérica: não revelar se a matrícula existe
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Matrícula ou senha inválidas",
    )
    aluno = db.scalar(
        select(Aluno).where(Aluno.matricula == payload.matricula.strip().upper())
    )
    if aluno is None or not aluno.ativo or not verificar_senha(payload.senha, aluno.senha_hash):
        raise erro
    return _emitir_tokens(db, aluno)


@router.post("/refresh", response_model=TokenOut)
def refresh(payload: RefreshIn, db: Session = Depends(get_db)) -> TokenOut:
    agora = datetime.now(UTC)
    token_h = hash_token(payload.refresh_token)
    registro = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_h))

    def _aware(dt: datetime) -> datetime:
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)

    if registro is None or registro.revogado or _aware(registro.expira_em) < agora:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    aluno = db.get(Aluno, registro.aluno_id)
    if aluno is None or not aluno.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    # Rotação: revoga o atual e emite outro
    registro.revogado = True
    db.add(registro)
    db.commit()
    return _emitir_tokens(db, aluno)


@router.post("/logout", response_model=MessageOut)
def logout(payload: LogoutIn, db: Session = Depends(get_db)) -> MessageOut:
    token_h = hash_token(payload.refresh_token)
    registro = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_h))
    if registro is not None and not registro.revogado:
        registro.revogado = True
        db.add(registro)
        db.commit()
    return MessageOut(detail="Sessão encerrada")
