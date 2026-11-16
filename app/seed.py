"""Popula o banco com dados 100% fictícios (só se estiver vazio)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Aluno,
    Chamado,
    ChamadoEvento,
    Curso,
    Disciplina,
    Historico,
    Parcela,
)
from app.security import hash_senha

# Senha de demonstração (documentada no README na fase 4)
SENHA_DEMO = "demo1234"

# Disciplinas do curso ADS — alinhadas ao protótipo
DISCIPLINAS = [
    # semestre, codigo, nome, carga
    (1, "DS101", "LÓGICA DE PROGRAMAÇÃO", 80),
    (1, "DS102", "ALGORITMOS", 80),
    (1, "DS103", "MATEMÁTICA DISCRETA", 60),
    (1, "DS104", "COMUNICAÇÃO E EXPRESSÃO", 40),
    (1, "DS105", "FUNDAMENTOS DE COMPUTAÇÃO", 40),
    (2, "DS201", "PROGRAMAÇÃO ORIENTADA A OBJETOS", 80),
    (2, "DS202", "BANCO DE DADOS", 80),
    (2, "DS203", "ENGENHARIA DE SOFTWARE", 60),
    (2, "DS204", "REDES DE COMPUTADORES", 60),
    (2, "DS205", "ESTATÍSTICA APLICADA", 40),
    (3, "DS301", "DESENVOLVIMENTO WEB", 80),
    (3, "DS302", "PROGRAMAÇÃO PARA DISPOSITIVOS", 80),
    (3, "DS303", "SISTEMAS OPERACIONAIS", 60),
    (3, "DS304", "GESTÃO DE PROJETOS DE SOFTWARE", 40),
    (4, "DS401", "ARQUITETURA DE SOFTWARE", 80),
    (4, "DS402", "SEGURANÇA DA INFORMAÇÃO", 60),
    (4, "DS403", "QUALIDADE DE SOFTWARE", 40),
    (4, "DS404", "PROJETO INTEGRADOR", 80),
]

# Histórico do Aluno Exemplo (A000001): status, media, faltas, b1..b4, ano_grade
HISTORICO_EXEMPLO: dict[str, tuple] = {
    "DS101": ("APROVADO", 8.5, 2, 8.0, 8.5, 9.0, 8.5, "2025/1"),
    "DS102": ("APROVADO", 7.8, 4, 7.0, 8.0, 7.5, 8.7, "2025/1"),
    "DS103": ("APROVADO", 7.2, 4, 6.5, 7.0, 7.5, 7.8, "2025/1"),
    "DS104": ("APROVADO", 9.0, 0, 9.0, 8.5, 9.5, 9.0, "2025/1"),
    "DS105": ("APROVADO", 8.0, 2, 7.5, 8.0, 8.0, 8.5, "2025/1"),
    "DS201": ("APROVADO", 8.7, 2, 8.5, 8.8, 8.4, 9.1, "2025/2"),
    "DS202": ("APROVADO", 7.5, 4, 7.0, 7.4, 7.8, 7.8, "2025/2"),
    "DS203": ("APROVADO", 8.2, 2, 8.0, 8.4, 8.0, 8.4, "2025/2"),
    "DS204": ("APROVADO", 6.9, 6, 6.5, 7.0, 6.8, 7.3, "2025/2"),
    "DS205": ("APROVADO", 7.4, 2, 7.0, 7.2, 7.6, 7.8, "2025/2"),
    "DS301": ("APROVADO", 9.1, 0, 9.0, 9.2, 8.8, 9.4, "2026/1"),
    "DS302": ("APROVADO", 8.4, 2, 8.0, 8.6, 8.2, 8.8, "2026/1"),
    "DS303": ("APROVADO", 7.0, 4, 6.8, 7.2, 6.9, 7.1, "2026/1"),
    "DS304": ("APROVADO", 8.8, 0, 8.5, 9.0, 8.6, 9.1, "2026/1"),
    "DS401": ("CURSANDO", 7.6, 2, 7.2, 8.0, None, None, "2026/2"),
    # 9 faltas em 60h ≈ 70% de frequência (alerta < 75%)
    "DS402": ("CURSANDO", 8.1, 9, 8.0, 8.2, None, None, "2026/2"),
    "DS403": ("APROVADO", 9.0, 0, 8.8, 9.0, 9.2, 9.0, "2026/2"),
    "DS404": ("CURSANDO", 8.5, 2, 8.4, 8.6, None, None, "2026/2"),
}


def banco_vazio(db: Session) -> bool:
    total = db.scalar(select(func.count()).select_from(Curso)) or 0
    return total == 0


def seed(db: Session) -> None:
    """Cria 1 curso, 5 alunos, disciplinas, histórico, parcelas e chamados."""
    if not banco_vazio(db):
        return

    curso = Curso(nome="Análise e Desenvolvimento de Sistemas", codigo="ADS000")
    db.add(curso)
    db.flush()

    disciplinas: dict[str, Disciplina] = {}
    for semestre, codigo, nome, carga in DISCIPLINAS:
        disc = Disciplina(
            codigo=codigo,
            nome=nome,
            carga_horaria=carga,
            semestre=semestre,
            curso_id=curso.id,
        )
        db.add(disc)
        disciplinas[codigo] = disc
    db.flush()

    alunos_dados = [
        {
            "matricula": "A000001",
            "nome": "Aluno Exemplo",
            "email": "aluno.exemplo@email.com",
            "telefone": "(00) 00000-0000",
            "cpf": "000.000.000-00",
            "rg": "00.000.000-0",
            "sexo": "Não informado",
            "nascimento": "01/01/2000",
            "turma": "DS0A00",
            "campus": "Campus Central",
            "unidade": "Campus Central",
            "ingresso": "02/01/25",
            "ano_grade": "2025",
            "ano_letivo": "2026",
            "status": "Ativo",
            "validade_carteira": "31/01/2027",
            "logradouro": "Rua Exemplo, 100",
            "complemento": "Apto 00",
            "bairro": "Bairro Exemplo",
            "cep": "00000-000",
            "cidade_uf": "Cidade Exemplo/EX",
        },
        {
            "matricula": "A000002",
            "nome": "Maria Demonstração",
            "email": "maria.demo@email.com",
            "telefone": "(11) 90000-0002",
            "cpf": "111.111.111-11",
            "rg": "11.111.111-1",
            "sexo": "Feminino",
            "nascimento": "15/03/1999",
            "turma": "DS0A00",
            "campus": "Campus Central",
            "unidade": "Campus Central",
            "ingresso": "02/01/25",
            "ano_grade": "2025",
            "ano_letivo": "2026",
            "status": "Ativo",
            "validade_carteira": "31/01/2027",
            "logradouro": "Av. Fictícia, 200",
            "complemento": "",
            "bairro": "Centro Exemplo",
            "cep": "11111-111",
            "cidade_uf": "Cidade Exemplo/EX",
        },
        {
            "matricula": "A000003",
            "nome": "João Demonstração",
            "email": "joao.demo@email.com",
            "telefone": "(11) 90000-0003",
            "cpf": "222.222.222-22",
            "rg": "22.222.222-2",
            "sexo": "Masculino",
            "nascimento": "20/07/2001",
            "turma": "DS0B00",
            "campus": "Campus Central",
            "unidade": "Campus Central",
            "ingresso": "01/08/25",
            "ano_grade": "2025",
            "ano_letivo": "2026",
            "status": "Ativo",
            "validade_carteira": "31/01/2027",
            "logradouro": "Rua Teste, 50",
            "complemento": "Casa 1",
            "bairro": "Jardim Exemplo",
            "cep": "22222-222",
            "cidade_uf": "Cidade Exemplo/EX",
        },
        {
            "matricula": "A000004",
            "nome": "Ana Demonstração",
            "email": "ana.demo@email.com",
            "telefone": "(11) 90000-0004",
            "cpf": "333.333.333-33",
            "rg": "33.333.333-3",
            "sexo": "Feminino",
            "nascimento": "08/11/2000",
            "turma": "DS0B00",
            "campus": "Campus Norte",
            "unidade": "Campus Norte",
            "ingresso": "02/01/24",
            "ano_grade": "2024",
            "ano_letivo": "2026",
            "status": "Ativo",
            "validade_carteira": "31/01/2027",
            "logradouro": "Travessa Sample, 12",
            "complemento": "Bloco B",
            "bairro": "Vila Exemplo",
            "cep": "33333-333",
            "cidade_uf": "Cidade Exemplo/EX",
        },
        {
            "matricula": "A000005",
            "nome": "Pedro Demonstração",
            "email": "pedro.demo@email.com",
            "telefone": "(11) 90000-0005",
            "cpf": "444.444.444-44",
            "rg": "44.444.444-4",
            "sexo": "Masculino",
            "nascimento": "30/05/1998",
            "turma": "DS0A00",
            "campus": "Campus Central",
            "unidade": "Campus Central",
            "ingresso": "02/01/25",
            "ano_grade": "2025",
            "ano_letivo": "2026",
            "status": "Ativo",
            "validade_carteira": "31/01/2027",
            "logradouro": "Alameda Demo, 9",
            "complemento": "Apto 101",
            "bairro": "Bairro Alpha",
            "cep": "44444-444",
            "cidade_uf": "Cidade Exemplo/EX",
        },
    ]

    senha = hash_senha(SENHA_DEMO)
    alunos: dict[str, Aluno] = {}
    for dados in alunos_dados:
        aluno = Aluno(curso_id=curso.id, senha_hash=senha, ativo=True, **dados)
        db.add(aluno)
        alunos[dados["matricula"]] = aluno
    db.flush()

    # Histórico completo só para A000001; demais ganham o 1º semestre aprovado
    for codigo, meta in HISTORICO_EXEMPLO.items():
        status, media, faltas, b1, b2, b3, b4, ano = meta
        db.add(
            Historico(
                aluno_id=alunos["A000001"].id,
                disciplina_id=disciplinas[codigo].id,
                ano_grade=ano,
                status=status,
                media_final=media,
                faltas=faltas,
                nota_b1=b1,
                nota_b2=b2,
                nota_b3=b3,
                nota_b4=b4,
            )
        )

    for mat in ("A000002", "A000003", "A000004", "A000005"):
        for semestre, codigo, _nome, _carga in DISCIPLINAS:
            if semestre != 1:
                continue
            db.add(
                Historico(
                    aluno_id=alunos[mat].id,
                    disciplina_id=disciplinas[codigo].id,
                    ano_grade="2025/1",
                    status="APROVADO",
                    media_final=7.5,
                    faltas=2,
                    nota_b1=7.0,
                    nota_b2=7.5,
                    nota_b3=7.5,
                    nota_b4=8.0,
                )
            )

    for mat, aluno in alunos.items():
        db.add(
            Parcela(
                aluno_id=aluno.id,
                referencia="05/06",
                valor_documento=980.0,
                valor_pagar=890.0,
                vencimento=date(2026, 12, 10),
                antecipacao_ate=date(2026, 11, 30),
                status="EM ABERTO",
            )
        )

    # Chamados de exemplo do Aluno Exemplo
    exemplos = [
        (
            "CH-20260001",
            "Coordenação",
            "Revisão de nota",
            "alta",
            "Pedido de revisão da média de Redes de Computadores.",
            "aberto",
            ["Chamado registrado", "Encaminhado ao setor Coordenação"],
        ),
        (
            "CH-20260002",
            "Financeiro",
            "Segunda via de boleto",
            "media",
            "Preciso da segunda via da mensalidade 05/06 para pagamento.",
            "andamento",
            [
                "Chamado registrado",
                "Encaminhado ao setor Financeiro",
                "Em análise pela equipe",
            ],
        ),
        (
            "CH-20260003",
            "Secretaria",
            "Declaração de vínculo",
            "baixa",
            "Solicito declaração de vínculo atualizada para estágio.",
            "resolvido",
            [
                "Chamado registrado",
                "Encaminhado ao setor Secretaria",
                "Em análise pela equipe",
                "Resolvido",
            ],
        ),
    ]
    for protocolo, setor, tipo, urgencia, descricao, status, eventos in exemplos:
        chamado = Chamado(
            protocolo=protocolo,
            aluno_id=alunos["A000001"].id,
            setor=setor,
            tipo=tipo,
            urgencia=urgencia,
            descricao=descricao,
            status=status,
        )
        db.add(chamado)
        db.flush()
        for texto in eventos:
            db.add(ChamadoEvento(chamado_id=chamado.id, descricao=texto))

    db.commit()
