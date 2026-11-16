"""Schemas Pydantic v2 — entrada e saída da API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LoginIn(BaseModel):
    matricula: str = Field(min_length=1, max_length=32)
    senha: str = Field(min_length=1, max_length=128)


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=10)


class LogoutIn(BaseModel):
    refresh_token: str = Field(min_length=10)


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class CursoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    codigo: str


class MeOut(BaseModel):
    id: int
    matricula: str
    nome: str
    email: str
    telefone: str
    cpf: str
    rg: str
    sexo: str
    nascimento: str
    turma: str
    campus: str
    unidade: str
    ingresso: str
    ano_grade: str
    ano_letivo: str
    status: str
    validade_carteira: str
    logradouro: str
    complemento: str
    bairro: str
    cep: str
    cidade_uf: str
    curso: CursoResumo


class CarteiraOut(BaseModel):
    nome: str
    matricula: str
    curso: str
    campus: str
    turma: str
    status: str
    validade_carteira: str
    progresso_percentual: int
    gerado_em: str
    qr_svg: str
    qr_token_expira_em: str


class ParcelaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    referencia: str
    valor_documento: float
    valor_pagar: float
    vencimento: date
    antecipacao_ate: date
    status: str


class DisciplinaIntegralizacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    nome: str
    carga_horaria: int
    semestre: int
    ano_grade: str
    status: str
    media_final: float | None


class NotaDisciplinaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    nome: str
    status: str
    media: float | None
    faltas: int
    frequencia: int
    notas: list[float | None]


class ChamadoCreateIn(BaseModel):
    setor: str = Field(min_length=2, max_length=80)
    tipo: str = Field(min_length=2, max_length=80)
    urgencia: Literal["baixa", "media", "alta"]
    descricao: str = Field(min_length=8, max_length=400)


class ChamadoEventoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    descricao: str
    criado_em: datetime


class ChamadoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    protocolo: str
    setor: str
    tipo: str
    urgencia: str
    descricao: str
    status: str
    criado_em: datetime
    atualizado_em: datetime


class ChamadoDetalheOut(ChamadoOut):
    eventos: list[ChamadoEventoOut]


class HealthOut(BaseModel):
    status: str
    env: str


class MessageOut(BaseModel):
    detail: str
