"""PDF fictício de atestado de matrícula (fpdf2)."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO

from fpdf import FPDF

from app.models import Aluno


def gerar_atestado_pdf(aluno: Aluno) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_margins(18, 18, 18)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "UniApp", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Portal do aluno (documento ficticio)", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Atestado de Matricula", ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Helvetica", "", 11)
    texto = (
        f"Atestamos, para os devidos fins, que {aluno.nome}, "
        f"matricula {aluno.matricula}, encontra-se com vinculo {aluno.status.lower()} "
        f"no curso {aluno.curso.nome} ({aluno.curso.codigo}), "
        f"turma {aluno.turma}, unidade {aluno.unidade}, campus {aluno.campus}."
    )
    pdf.multi_cell(0, 7, texto)
    pdf.ln(4)

    linhas = [
        f"Ingresso: {aluno.ingresso}",
        f"Ano/grade: {aluno.ano_grade}",
        f"Ano letivo: {aluno.ano_letivo}",
        f"Validade da carteira: {aluno.validade_carteira}",
        f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
    ]
    for linha in linhas:
        pdf.cell(0, 7, linha, ln=True)

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        0,
        5,
        "Documento gerado automaticamente para demonstracao do UniApp. "
        "Nao possui validade oficial e nao representa instituicao real.",
    )

    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
