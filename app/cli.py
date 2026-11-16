"""CLI para cadastro manual de alunos (argparse)."""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import select

from app.db import SessionLocal, init_db
from app.models import Aluno, Curso
from app.security import hash_senha


def _db():
    init_db()
    return SessionLocal()


def cmd_criar_aluno(args: argparse.Namespace) -> int:
    db = _db()
    try:
        if db.scalar(select(Aluno).where(Aluno.matricula == args.matricula.upper())):
            print(f"Erro: matrícula {args.matricula.upper()} já existe.", file=sys.stderr)
            return 1
        curso = db.scalar(select(Curso).where(Curso.codigo == args.curso))
        if curso is None:
            print(f"Erro: curso '{args.curso}' não encontrado.", file=sys.stderr)
            return 1
        aluno = Aluno(
            matricula=args.matricula.upper(),
            nome=args.nome,
            senha_hash=hash_senha(args.senha),
            email=args.email,
            telefone=args.telefone,
            cpf=args.cpf,
            rg=args.rg,
            sexo=args.sexo,
            nascimento=args.nascimento,
            curso_id=curso.id,
            turma=args.turma,
            campus=args.campus,
            unidade=args.unidade,
            ingresso=args.ingresso,
            ano_grade=args.ano_grade,
            ano_letivo=args.ano_letivo,
            status=args.status,
            validade_carteira=args.validade,
            logradouro=args.logradouro,
            complemento=args.complemento,
            bairro=args.bairro,
            cep=args.cep,
            cidade_uf=args.cidade_uf,
            ativo=True,
        )
        db.add(aluno)
        db.commit()
        print(f"Aluno criado: {aluno.matricula} — {aluno.nome}")
        return 0
    finally:
        db.close()


def cmd_resetar_senha(args: argparse.Namespace) -> int:
    db = _db()
    try:
        aluno = db.scalar(select(Aluno).where(Aluno.matricula == args.matricula.upper()))
        if aluno is None:
            print("Erro: aluno não encontrado.", file=sys.stderr)
            return 1
        aluno.senha_hash = hash_senha(args.senha)
        db.add(aluno)
        db.commit()
        print(f"Senha redefinida para {aluno.matricula}")
        return 0
    finally:
        db.close()


def cmd_listar_alunos(_args: argparse.Namespace) -> int:
    db = _db()
    try:
        alunos = db.scalars(select(Aluno).order_by(Aluno.matricula.asc())).all()
        if not alunos:
            print("Nenhum aluno cadastrado.")
            return 0
        for a in alunos:
            estado = "ativo" if a.ativo else "inativo"
            print(f"{a.matricula}\t{a.nome}\t{a.email}\t{estado}")
        return 0
    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description="CLI UniApp")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_criar = sub.add_parser("criar-aluno", help="Cadastra um aluno fictício")
    p_criar.add_argument("--matricula", required=True)
    p_criar.add_argument("--nome", required=True)
    p_criar.add_argument("--senha", required=True)
    p_criar.add_argument("--email", required=True)
    p_criar.add_argument("--curso", default="ADS000", help="Código do curso")
    p_criar.add_argument("--telefone", default="(00) 00000-0000")
    p_criar.add_argument("--cpf", default="000.000.000-00")
    p_criar.add_argument("--rg", default="00.000.000-0")
    p_criar.add_argument("--sexo", default="Não informado")
    p_criar.add_argument("--nascimento", default="01/01/2000")
    p_criar.add_argument("--turma", default="DS0A00")
    p_criar.add_argument("--campus", default="Campus Central")
    p_criar.add_argument("--unidade", default="Campus Central")
    p_criar.add_argument("--ingresso", default="02/01/25")
    p_criar.add_argument("--ano-grade", dest="ano_grade", default="2025")
    p_criar.add_argument("--ano-letivo", dest="ano_letivo", default="2026")
    p_criar.add_argument("--status", default="Ativo")
    p_criar.add_argument("--validade", default="31/01/2027")
    p_criar.add_argument("--logradouro", default="Rua Exemplo, 100")
    p_criar.add_argument("--complemento", default="")
    p_criar.add_argument("--bairro", default="Bairro Exemplo")
    p_criar.add_argument("--cep", default="00000-000")
    p_criar.add_argument("--cidade-uf", dest="cidade_uf", default="Cidade Exemplo/EX")
    p_criar.set_defaults(func=cmd_criar_aluno)

    p_reset = sub.add_parser("resetar-senha", help="Redefine a senha de um aluno")
    p_reset.add_argument("--matricula", required=True)
    p_reset.add_argument("--senha", required=True)
    p_reset.set_defaults(func=cmd_resetar_senha)

    p_list = sub.add_parser("listar-alunos", help="Lista matrícula, nome e e-mail")
    p_list.set_defaults(func=cmd_listar_alunos)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
