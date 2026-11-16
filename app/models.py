"""Modelos SQLAlchemy — dados fictícios do UniApp."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    codigo: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)

    alunos: Mapped[list[Aluno]] = relationship(back_populates="curso")
    disciplinas: Mapped[list[Disciplina]] = relationship(back_populates="curso")


class Aluno(Base):
    __tablename__ = "alunos"
    __table_args__ = (Index("ix_alunos_matricula_ativo", "matricula", "ativo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    matricula: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(160), nullable=False)
    telefone: Mapped[str] = mapped_column(String(32), nullable=False)
    cpf: Mapped[str] = mapped_column(String(20), nullable=False)
    rg: Mapped[str] = mapped_column(String(20), nullable=False)
    sexo: Mapped[str] = mapped_column(String(40), nullable=False)
    nascimento: Mapped[str] = mapped_column(String(20), nullable=False)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"), nullable=False, index=True)
    turma: Mapped[str] = mapped_column(String(32), nullable=False)
    campus: Mapped[str] = mapped_column(String(80), nullable=False)
    unidade: Mapped[str] = mapped_column(String(80), nullable=False)
    ingresso: Mapped[str] = mapped_column(String(20), nullable=False)
    ano_grade: Mapped[str] = mapped_column(String(16), nullable=False)
    ano_letivo: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="Ativo")
    validade_carteira: Mapped[str] = mapped_column(String(20), nullable=False)
    logradouro: Mapped[str] = mapped_column(String(160), nullable=False)
    complemento: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    bairro: Mapped[str] = mapped_column(String(80), nullable=False)
    cep: Mapped[str] = mapped_column(String(16), nullable=False)
    cidade_uf: Mapped[str] = mapped_column(String(80), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    curso: Mapped[Curso] = relationship(back_populates="alunos")
    historicos: Mapped[list[Historico]] = relationship(back_populates="aluno")
    parcelas: Mapped[list[Parcela]] = relationship(back_populates="aluno")
    chamados: Mapped[list[Chamado]] = relationship(back_populates="aluno")
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(back_populates="aluno")


class Disciplina(Base):
    __tablename__ = "disciplinas"
    __table_args__ = (
        UniqueConstraint("codigo", "curso_id", name="uq_disciplina_codigo_curso"),
        Index("ix_disciplinas_curso_semestre", "curso_id", "semestre"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    carga_horaria: Mapped[int] = mapped_column(Integer, nullable=False)
    semestre: Mapped[int] = mapped_column(Integer, nullable=False)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"), nullable=False, index=True)

    curso: Mapped[Curso] = relationship(back_populates="disciplinas")
    historicos: Mapped[list[Historico]] = relationship(back_populates="disciplina")


class Historico(Base):
    __tablename__ = "historico"
    __table_args__ = (
        UniqueConstraint("aluno_id", "disciplina_id", name="uq_historico_aluno_disciplina"),
        Index("ix_historico_aluno", "aluno_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"), nullable=False)
    disciplina_id: Mapped[int] = mapped_column(ForeignKey("disciplinas.id"), nullable=False)
    ano_grade: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    media_final: Mapped[float | None] = mapped_column(Float, nullable=True)
    faltas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nota_b1: Mapped[float | None] = mapped_column(Float, nullable=True)
    nota_b2: Mapped[float | None] = mapped_column(Float, nullable=True)
    nota_b3: Mapped[float | None] = mapped_column(Float, nullable=True)
    nota_b4: Mapped[float | None] = mapped_column(Float, nullable=True)

    aluno: Mapped[Aluno] = relationship(back_populates="historicos")
    disciplina: Mapped[Disciplina] = relationship(back_populates="historicos")


class Parcela(Base):
    __tablename__ = "parcelas"
    __table_args__ = (Index("ix_parcelas_aluno_status", "aluno_id", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"), nullable=False)
    referencia: Mapped[str] = mapped_column(String(16), nullable=False)
    valor_documento: Mapped[float] = mapped_column(Float, nullable=False)
    valor_pagar: Mapped[float] = mapped_column(Float, nullable=False)
    vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    antecipacao_ate: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="EM ABERTO")

    aluno: Mapped[Aluno] = relationship(back_populates="parcelas")


class Chamado(Base):
    __tablename__ = "chamados"
    __table_args__ = (Index("ix_chamados_aluno_status", "aluno_id", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    protocolo: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"), nullable=False)
    setor: Mapped[str] = mapped_column(String(80), nullable=False)
    tipo: Mapped[str] = mapped_column(String(80), nullable=False)
    urgencia: Mapped[str] = mapped_column(String(16), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="aberto")
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    aluno: Mapped[Aluno] = relationship(back_populates="chamados")
    eventos: Mapped[list[ChamadoEvento]] = relationship(
        back_populates="chamado",
        order_by="ChamadoEvento.criado_em",
        cascade="all, delete-orphan",
    )


class ChamadoEvento(Base):
    __tablename__ = "chamado_eventos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chamado_id: Mapped[int] = mapped_column(ForeignKey("chamados.id"), nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    chamado: Mapped[Chamado] = relationship(back_populates="eventos")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (Index("ix_refresh_aluno_revogado", "aluno_id", "revogado"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revogado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    aluno: Mapped[Aluno] = relationship(back_populates="refresh_tokens")
