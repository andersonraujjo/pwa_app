"""Gera QR da carteirinha (SVG via segno) com token assinado de curta duração."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import segno

from app.security import criar_token_carteira


def gerar_qr_carteira(*, aluno_id: int, matricula: str) -> tuple[str, str, str]:
    """
    Retorna (qr_svg, gerado_em_formatado, qr_token_expira_em_iso).
    O conteúdo do QR é um payload fictício + JWT curto (não é dado real).
    """
    minutos = 5
    token = criar_token_carteira(aluno_id=aluno_id, matricula=matricula, minutos=minutos)
    agora = datetime.now(UTC)
    expira = agora + timedelta(minutes=minutos)
    payload = f"UNIAPP|{matricula}|{token}"
    qr = segno.make(payload, error="m")
    svg = qr.svg_inline(scale=6, dark="#0A1466", light="#ffffff")
    gerado_em = agora.astimezone().strftime("%d/%m/%Y %H:%M")
    return svg, gerado_em, expira.isoformat()
