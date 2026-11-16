"""Rotas /api/me/* — sempre escopadas ao aluno do JWT."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.deps import get_current_aluno
from app.models import Aluno, Chamado, ChamadoEvento, Disciplina, Historico, Parcela
from app.schemas import (
    CarteiraOut,
    ChamadoCreateIn,
    ChamadoDetalheOut,
    ChamadoEventoOut,
    ChamadoOut,
    CursoResumo,
    DisciplinaIntegralizacaoOut,
    MeOut,
    NotaDisciplinaOut,
    ParcelaOut,
)
from app.services.academico import calcular_frequencia, progresso_curso
from app.services.atestado_pdf import gerar_atestado_pdf
from app.services.carteira_qr import gerar_qr_carteira

router = APIRouter(prefix="/me", tags=["me"])


def _me_out(aluno: Aluno) -> MeOut:
    return MeOut(
        id=aluno.id,
        matricula=aluno.matricula,
        nome=aluno.nome,
        email=aluno.email,
        telefone=aluno.telefone,
        cpf=aluno.cpf,
        rg=aluno.rg,
        sexo=aluno.sexo,
        nascimento=aluno.nascimento,
        turma=aluno.turma,
        campus=aluno.campus,
        unidade=aluno.unidade,
        ingresso=aluno.ingresso,
        ano_grade=aluno.ano_grade,
        ano_letivo=aluno.ano_letivo,
        status=aluno.status,
        validade_carteira=aluno.validade_carteira,
        logradouro=aluno.logradouro,
        complemento=aluno.complemento,
        bairro=aluno.bairro,
        cep=aluno.cep,
        cidade_uf=aluno.cidade_uf,
        curso=CursoResumo.model_validate(aluno.curso),
    )


@router.get("", response_model=MeOut)
def ler_me(aluno: Aluno = Depends(get_current_aluno)) -> MeOut:
    return _me_out(aluno)


@router.get("/carteira", response_model=CarteiraOut)
def ler_carteira(
    aluno: Aluno = Depends(get_current_aluno),
    db: Session = Depends(get_db),
) -> CarteiraOut:
    historicos = list(
        db.scalars(select(Historico).where(Historico.aluno_id == aluno.id)).all()
    )
    qr_svg, gerado_em, expira = gerar_qr_carteira(
        aluno_id=aluno.id, matricula=aluno.matricula
    )
    return CarteiraOut(
        nome=aluno.nome,
        matricula=aluno.matricula,
        curso=aluno.curso.nome,
        campus=aluno.campus,
        turma=aluno.turma,
        status=aluno.status,
        validade_carteira=aluno.validade_carteira,
        progresso_percentual=progresso_curso(historicos),
        gerado_em=gerado_em,
        qr_svg=qr_svg,
        qr_token_expira_em=expira,
    )


@router.get("/pagamentos", response_model=list[ParcelaOut])
def listar_pagamentos(
    aluno: Aluno = Depends(get_current_aluno),
    db: Session = Depends(get_db),
) -> list[ParcelaOut]:
    parcelas = db.scalars(
        select(Parcela)
        .where(Parcela.aluno_id == aluno.id)
        .order_by(Parcela.vencimento.asc())
    ).all()
    return [ParcelaOut.model_validate(p) for p in parcelas]


@router.get("/disciplinas", response_model=list[DisciplinaIntegralizacaoOut])
def listar_disciplinas(
    semestre: int = Query(..., ge=1, le=4),
    aluno: Aluno = Depends(get_current_aluno),
    db: Session = Depends(get_db),
) -> list[DisciplinaIntegralizacaoOut]:
    rows = db.execute(
        select(Historico, Disciplina)
        .join(Disciplina, Historico.disciplina_id == Disciplina.id)
        .where(
            Historico.aluno_id == aluno.id,
            Disciplina.semestre == semestre,
            Disciplina.curso_id == aluno.curso_id,
        )
        .order_by(Disciplina.codigo.asc())
    ).all()
    return [
        DisciplinaIntegralizacaoOut(
            codigo=disc.codigo,
            nome=disc.nome,
            carga_horaria=disc.carga_horaria,
            semestre=disc.semestre,
            ano_grade=hist.ano_grade,
            status=hist.status,
            media_final=hist.media_final,
        )
        for hist, disc in rows
    ]


@router.get("/notas", response_model=list[NotaDisciplinaOut])
def listar_notas(
    aluno: Aluno = Depends(get_current_aluno),
    db: Session = Depends(get_db),
) -> list[NotaDisciplinaOut]:
    rows = db.execute(
        select(Historico, Disciplina)
        .join(Disciplina, Historico.disciplina_id == Disciplina.id)
        .where(Historico.aluno_id == aluno.id)
        .order_by(Disciplina.semestre.asc(), Disciplina.codigo.asc())
    ).all()
    saida: list[NotaDisciplinaOut] = []
    for hist, disc in rows:
        saida.append(
            NotaDisciplinaOut(
                codigo=disc.codigo,
                nome=disc.nome,
                status=hist.status,
                media=hist.media_final,
                faltas=hist.faltas,
                frequencia=calcular_frequencia(hist.faltas, disc.carga_horaria),
                notas=[hist.nota_b1, hist.nota_b2, hist.nota_b3, hist.nota_b4],
            )
        )
    return saida


@router.get("/atestado")
def baixar_atestado(aluno: Aluno = Depends(get_current_aluno)) -> Response:
    pdf = gerar_atestado_pdf(aluno)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'inline; filename="AtestadoMatricula.pdf"',
        },
    )


@router.get("/chamados", response_model=list[ChamadoOut])
def listar_chamados(
    aluno: Aluno = Depends(get_current_aluno),
    db: Session = Depends(get_db),
) -> list[ChamadoOut]:
    itens = db.scalars(
        select(Chamado)
        .where(Chamado.aluno_id == aluno.id)
        .order_by(Chamado.criado_em.desc())
    ).all()
    return [ChamadoOut.model_validate(c) for c in itens]


def _proximo_protocolo(db: Session) -> str:
    # CH-YYYYNNNN — único o bastante para o protótipo
    ano = datetime.now(UTC).year
    prefixo = f"CH-{ano}"
    total = db.scalar(select(func.count()).select_from(Chamado)) or 0
    return f"{prefixo}{total + 1:04d}"


@router.post("/chamados", response_model=ChamadoDetalheOut, status_code=status.HTTP_201_CREATED)
def criar_chamado(
    payload: ChamadoCreateIn,
    aluno: Aluno = Depends(get_current_aluno),
    db: Session = Depends(get_db),
) -> ChamadoDetalheOut:
    protocolo = _proximo_protocolo(db)
    # Garante unicidade sob concorrência leve
    while db.scalar(select(Chamado.id).where(Chamado.protocolo == protocolo)):
        protocolo = _proximo_protocolo(db)

    chamado = Chamado(
        protocolo=protocolo,
        aluno_id=aluno.id,
        setor=payload.setor.strip(),
        tipo=payload.tipo.strip(),
        urgencia=payload.urgencia,
        descricao=payload.descricao.strip(),
        status="aberto",
    )
    db.add(chamado)
    db.flush()
    db.add(ChamadoEvento(chamado_id=chamado.id, descricao="Chamado registrado"))
    db.add(
        ChamadoEvento(
            chamado_id=chamado.id,
            descricao=f"Encaminhado ao setor {chamado.setor}",
        )
    )
    db.commit()
    db.refresh(chamado)
    chamado = db.scalar(
        select(Chamado)
        .options(selectinload(Chamado.eventos))
        .where(Chamado.id == chamado.id)
    )
    assert chamado is not None
    return ChamadoDetalheOut(
        **ChamadoOut.model_validate(chamado).model_dump(),
        eventos=[ChamadoEventoOut.model_validate(e) for e in chamado.eventos],
    )


@router.get("/chamados/{chamado_id}", response_model=ChamadoDetalheOut)
def detalhe_chamado(
    chamado_id: int,
    aluno: Aluno = Depends(get_current_aluno),
    db: Session = Depends(get_db),
) -> ChamadoDetalheOut:
    chamado = db.scalar(
        select(Chamado)
        .options(selectinload(Chamado.eventos))
        .where(Chamado.id == chamado_id, Chamado.aluno_id == aluno.id)
    )
    if chamado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado")
    return ChamadoDetalheOut(
        **ChamadoOut.model_validate(chamado).model_dump(),
        eventos=[ChamadoEventoOut.model_validate(e) for e in chamado.eventos],
    )
