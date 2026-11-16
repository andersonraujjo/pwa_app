"""Gera static/index.html a partir do protótipo (Fase 2)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "index.html").read_text(encoding="utf-8")
body_start = src.index("<body>")
body = src[body_start:]

login = """
    <section class="screen" id="screen-login" aria-hidden="true">
      <form class="login-card" id="formLogin" novalidate>
        <p class="login-kicker">Acesso do aluno</p>
        <h2>Entrar</h2>
        <label class="lbl">Matrícula
          <input type="text" name="matricula" id="loginMatricula" autocomplete="username" maxlength="32" placeholder="Ex.: A000001" required>
        </label>
        <label class="lbl">Senha
          <span class="senha-wrap">
            <input type="password" name="senha" id="loginSenha" autocomplete="current-password" maxlength="128" placeholder="Sua senha" required>
            <button type="button" class="toggle-senha" id="toggleSenha" data-action="toggle-senha" aria-label="Mostrar ou ocultar senha">Ver</button>
          </span>
        </label>
        <p class="login-erro" id="loginErro" hidden></p>
        <button type="submit" class="btn btn-navy" id="btnLogin">Entrar</button>
        <p class="login-hint">Demonstração: A000001 / demo1234<br>TODO fase 2: WebAuthn</p>
      </form>
    </section>
"""

body = re.sub(
    r'<section class="screen" id="screen-biometria".*?</section>\s*',
    login,
    body,
    count=1,
    flags=re.S,
)

body = body.replace(
    '<canvas id="qrCanvas" width="210" height="210" aria-label="Código visual fictício da carteirinha"></canvas>',
    '<div id="qrHost" aria-label="QR code da carteirinha"></div>',
)

body, n_pay = re.subn(
    r'(<div class="screen-body">\s*<h2 class="sec-title">Parcelas em aberto</h2>\s*)'
    r'<article class="card">.*?</article>\s*'
    r'(</div>\s*</section>\s*\n\s*<section class="screen" id="screen-atestado")',
    r'\1<div id="pagamentosLista"></div>\n      \2',
    body,
    count=1,
    flags=re.S,
)

body = body.replace("<span>PDF · 126 KB</span>", '<span id="atestadoMeta">PDF</span>', 1)

body = re.sub(r"\s*<script>.*?</script>\s*", "\n", body, count=1, flags=re.S)

scripts = """
  <script src="/js/api.js" defer></script>
  <script src="/js/app.js" defer></script>
"""
if "</body>" in body:
    body = body.replace("</body>", scripts + "</body>", 1)
else:
    body += scripts

head = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#12208F">
  <meta name="description" content="UniApp — portal do aluno (dados fictícios).">
  <title>UniApp — Portal do aluno</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%2312208F'/%3E%3Ctext x='32' y='44' text-anchor='middle' font-size='30' font-family='Arial' font-weight='700' fill='%23FFD400'%3EU%3C/text%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/app.css">
</head>
"""

out = head + body
# Garante um único fechamento de html
out = re.sub(r"(</html>\s*)+$", "</html>\n", out)
if not out.rstrip().endswith("</html>"):
    out = out.rstrip() + "\n</html>\n"

dest = ROOT / "static" / "index.html"
dest.write_text(out, encoding="utf-8")
print("pay_replaced", n_pay)
print("wrote", dest)
print("login", "screen-login" in out)
print("biometria", "screen-biometria" in out)
print("qrHost", "qrHost" in out)
print("pagamentosLista", "pagamentosLista" in out)
