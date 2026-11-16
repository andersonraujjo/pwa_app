"""Regras acadêmicas simples usadas pela API."""

from __future__ import annotations

from app.models import Historico


def calcular_frequencia(faltas: int, carga_horaria: int) -> int:
    """
    Frequência aproximada: cada falta = 2h de aula.
    Mantém o alerta de < 75% coerente com o protótipo.
    """
    if carga_horaria <= 0:
        return 100
    horas_faltas = max(0, faltas) * 2
    pct = 100 * (1 - (horas_faltas / carga_horaria))
    return max(0, min(100, round(pct)))


def progresso_curso(historicos: list[Historico]) -> int:
    if not historicos:
        return 0
    aprovados = sum(1 for h in historicos if h.status.upper() == "APROVADO")
    return round(100 * aprovados / len(historicos))
