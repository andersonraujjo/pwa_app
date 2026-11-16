# UniApp — Portal do aluno (PWA)

Aplicativo acadêmico fictício (projeto de extensão): carteira estudantil, dados cadastrais, pagamentos, documentos, notas e chamados.  
**Nenhum dado, logo ou marca de instituição real.**

Stack: **FastAPI + SQLite + SQLAlchemy 2.0** no backend; front estático em `static/` com **PWA** (manifest + service worker).

### Telas

| Home | Carteira estudantil | Chamados |
|:----:|:-------------------:|:--------:|
| ![Home do UniApp](imgs/img.png) | ![Carteira estudantil](imgs/img2.png) | ![Chamados](imgs/img3.png) |

---

## Credenciais de demonstração

| Matrícula | Senha     | Nome              |
|-----------|-----------|-------------------|
| `A000001` | `demo1234` | Aluno Exemplo     |
| `A000002` … `A000005` | `demo1234` | Alunos demo |

O seed roda na subida se o banco estiver vazio e `SEED_ON_START=true`.

---

## Rodar local

Requisitos: Python 3.11+ (testado com 3.12/3.14).

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abra:

- App: http://127.0.0.1:8000/
- API docs: http://127.0.0.1:8000/docs

### Ícones PWA (opcional)

```bash
python scripts/gerar_icones.py
```

### CLI de alunos

```bash
python -m app.cli listar-alunos
python -m app.cli criar-aluno --matricula A000099 --nome "Novo Demo" --senha demo1234 --email novo@email.com
python -m app.cli resetar-senha --matricula A000001 --senha novaSenha123
```

### Testes

```bash
pip install -r requirements.txt
pytest -q
```

---

## Testar no celular (túnel HTTPS)

PWAs e service worker pedem **HTTPS** (ou `localhost`). No celular na mesma rede:

1. Suba o servidor com `--host 0.0.0.0`.
2. Exponha com um túnel HTTPS, por exemplo:

```bash
# exemplo com cloudflared (instale à parte)
cloudflared tunnel --url http://127.0.0.1:8000
```

3. Abra a URL `https://…` no Chrome/Safari do telefone.
4. Android/Chrome: use **Instalar app** (se o evento `beforeinstallprompt` aparecer).  
   iOS: **Compartilhar → Adicionar à Tela de Início**.

---

## Variáveis de ambiente

Veja `.env.example`:

| Variável | Descrição |
|----------|-----------|
| `ENV` | `development` ou `production` |
| `SECRET_KEY` | Chave JWT (obrigatória e não padrão se `ENV=production`) |
| `DATABASE_URL` | Padrão `sqlite:///./data/app.db` — troque para Postgres sem mudar código |
| `ACCESS_TOKEN_MINUTES` | Access token (padrão 15) |
| `REFRESH_TOKEN_DAYS` | Refresh token (padrão 7) |
| `ALLOWED_ORIGINS` | CORS; vazio = mesma origem apenas |
| `SEED_ON_START` | `true`/`false` — seed se banco vazio |

---

## Publicar em hospedagem gratuita (Render / Railway / Fly)

1. Conecte o repositório ou faça deploy da imagem Docker.
2. Defina `SECRET_KEY` (longo e aleatório).
3. Defina `PORT` conforme a plataforma (o `Dockerfile` já usa `$PORT`).
4. Comando típico:  
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers`
5. Disco: em planos gratuitos o **SQLite pode ser apagado** a cada redeploy/restart.  
   - Mantenha `SEED_ON_START=true` para recriar dados demo, **ou**  
   - Use um volume persistente / migre para Postgres (abaixo).

### Docker local

```bash
docker build -t uniapp .
docker run --rm -p 8000:8000 -e SECRET_KEY=uma-chave-longa-de-demo uniapp
```

---

## Migrar para VPS / Hostinger e Postgres

1. **Banco:** crie um Postgres e aponte:

```env
ENV=production
SECRET_KEY=gera-uma-chave-forte
DATABASE_URL=postgresql+psycopg://USER:SENHA@HOST:5432/uniapp
SEED_ON_START=false
```

Instale o driver (`pip install psycopg[binary]`) ou use a URL compatível com o dialeto SQLAlchemy escolhido. O código já lê só `DATABASE_URL` — **não precisa alterar models** para a troca básica.

2. **App com Gunicorn + Uvicorn workers:**

```bash
pip install gunicorn
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 --workers 2 --proxy-headers
```

3. **Nginx** (TLS + proxy):

```nginx
server {
    listen 443 ssl;
    server_name seu-dominio.com;
    # ssl_certificate ...;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **systemd** (exemplo):

```ini
[Unit]
Description=UniApp
After=network.target

[Service]
WorkingDirectory=/var/www/uniapp
EnvironmentFile=/var/www/uniapp/.env
ExecStart=/var/www/uniapp/.venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 --workers 2 --proxy-headers
Restart=always

[Install]
WantedBy=multi-user.target
```

5. Rode o CLI/`seed` uma vez no Postgres se precisar dos alunos demo, ou cadastre com `python -m app.cli criar-aluno …`.

---

## Estrutura

```
app/                 # FastAPI, models, seed, CLI, routers
static/              # PWA: index, css, js, sw.js, manifest, icons
scripts/gerar_icones.py
tests/               # pytest
Dockerfile
requirements.txt
.env.example
```

---

## Avisos

- Dados 100% fictícios.
- Disco efêmero + SQLite em free tier = perda de dados; use seed ou Postgres.
- Em `production`, o app **não sobe** com `SECRET_KEY` padrão.
