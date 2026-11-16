Você é um engenheiro full-stack sênior. Vou te passar um protótipo clicável de app acadêmico mobile, em um único arquivo HTML (anexado/colado abaixo). Transforme-o em um PWA instalável com backend FastAPI + SQLite, mantendo EXATAMENTE o visual e as telas atuais. Entregue o projeto completo, com todos os arquivos prontos para rodar.

## DECISÕES JÁ TOMADAS
- Fase 1: hospedagem gratuita (ex.: Render/Railway/Fly); depois migração para VPS/Hostinger. Tudo deve funcionar sem mudar código, só variáveis de ambiente.
- Backend: FastAPI + SQLite com tabelas reais de alunos. O banco será trocado depois (Postgres/MySQL), então use SQLAlchemy 2.0 (síncrono) + Pydantic v2 e leia a conexão de DATABASE_URL (padrão: sqlite:///./data/app.db).
- Login: matrícula + senha, com JWT.
- Todos os dados são FICTÍCIOS. Nada de dados reais, nem de marca de instituição real.

## ESTRUTURA DO PROJETO
projeto/
  app/ (main.py, config.py, db.py, models.py, schemas.py, security.py, deps.py, seed.py, cli.py, routers/)
  static/ (index.html, css/, js/ com api.js e app.js, manifest.webmanifest, sw.js, offline.html, icons/)
  scripts/gerar_icones.py (Pillow: gera icon-192, icon-512, maskable-512 e apple-touch-icon 180 a partir de um desenho simples do logo "UniApp")
  tests/ (pytest)
  requirements.txt, Dockerfile, .env.example, .gitignore, README.md

## BANCO DE DADOS (SQLAlchemy)
- cursos(id, nome, codigo)
- alunos(id, matricula UNIQUE, nome, senha_hash, email, telefone, cpf, rg, sexo, nascimento, curso_id, turma, campus, unidade, ingresso, ano_grade, ano_letivo, status, validade_carteira, logradouro, complemento, bairro, cep, cidade_uf, ativo)
- disciplinas(id, codigo, nome, carga_horaria, semestre, curso_id)
- historico(id, aluno_id, disciplina_id, ano_grade, status, media_final, faltas, nota_b1, nota_b2, nota_b3, nota_b4)
- parcelas(id, aluno_id, referencia, valor_documento, valor_pagar, vencimento, antecipacao_ate, status)
- chamados(id, protocolo UNIQUE, aluno_id, setor, tipo, urgencia, descricao, status, criado_em, atualizado_em)
- chamado_eventos(id, chamado_id, descricao, criado_em)
- refresh_tokens(id, aluno_id, token_hash, expira_em, revogado)
Use índices nas colunas de busca, constraints e relacionamentos corretos.

## SEED E CLI
- seed.py cria 1 curso, 3 a 5 alunos fictícios (matrículas A000001 a A000005, senha de demonstração informada no README), disciplinas por semestre (1º ao 4º), histórico, parcelas e chamados de exemplo. Roda automaticamente na inicialização SOMENTE se o banco estiver vazio e SEED_ON_START=true (o disco de hospedagem gratuita pode ser apagado).
- cli.py (argparse ou typer): "criar-aluno", "resetar-senha", "listar-alunos", para eu cadastrar alunos manualmente.

## API (prefixo /api, JSON, documentação automática em /docs)
- GET /api/health
- POST /api/auth/login (matrícula + senha) -> access token (15 min) + refresh token (7 dias)
- POST /api/auth/refresh (com rotação do refresh token) e POST /api/auth/logout (revoga)
- GET /api/me (dados pessoais, acadêmicos e endereço)
- GET /api/me/carteira (dados da carteira + QR code como SVG gerado no servidor com a lib "segno", com um token assinado de curta duração dentro do QR + timestamp de geração)
- GET /api/me/pagamentos
- GET /api/me/disciplinas?semestre=1..4 (integralização curricular)
- GET /api/me/notas (notas e faltas por disciplina, com % de frequência)
- GET /api/me/atestado (PDF de atestado de matrícula gerado no servidor com reportlab ou fpdf2, dados fictícios, retorna application/pdf)
- GET /api/me/chamados, POST /api/me/chamados (gera protocolo único), GET /api/me/chamados/{id} (com linha do tempo)
Todas as rotas /api/me/* exigem Bearer JWT e só retornam dados do próprio aluno (checagem por aluno_id do token, nunca por id vindo da URL).

## SEGURANÇA
- Hash de senha com argon2 (lib argon2-cffi ou pwdlib); JWT com PyJWT; SECRET_KEY via ambiente (falhar ao iniciar em produção se estiver com valor padrão).
- Limite de tentativas de login (ex.: 5 por minuto por IP + matrícula, com slowapi ou implementação simples) e mensagem de erro genérica.
- Mesma origem (o FastAPI serve o front), CORS fechado por padrão com ALLOWED_ORIGINS configurável.
- Cabeçalhos de segurança (CSP básica, X-Content-Type-Options, Referrer-Policy). Não registrar dados pessoais em logs.
- Validação com Pydantic em todas as entradas; sem SQL cru.

## FRONT-END (manter o design atual)
- Extraia CSS e JS do HTML único para static/css e static/js, sem mudar o visual.
- Crie js/api.js: wrapper de fetch que anexa o Bearer token, renova automaticamente via refresh ao receber 401, trata erros de rede e aciona o overlay "CARREGANDO...".
- Substitua todos os dados mockados por chamadas à API.
- Troque a tela simulada de biometria por uma tela de LOGIN (matrícula + senha, mostrar/ocultar senha, mensagens de erro, estado de carregamento). Mantenha a sessão pelo refresh token e deixe um comentário "TODO fase 2: WebAuthn".
- Logout revoga o refresh token, limpa o estado e APAGA os caches de dados privados do service worker.
- Remova a moldura de celular quando for tela pequena ou quando estiver instalado (display-mode: standalone); no desktop larga, mantenha a moldura.
- Use viewport-fit=cover, 100dvh e env(safe-area-inset-*) para funcionar bem com notch no celular.

## PWA
- manifest.webmanifest: name, short_name, lang pt-BR, start_url "/", scope "/", display "standalone", theme_color e background_color coerentes com a identidade, ícones 192, 512 e maskable.
- Meta tags: theme-color, apple-mobile-web-app-capable, apple-touch-icon, apple-mobile-web-app-status-bar-style.
- sw.js (escopo "/"), com nome de cache versionado:
  - precache do app shell (HTML, CSS, JS, ícones, offline.html), com estratégia cache-first.
  - GET /api/me/* com stale-while-revalidate ou network-first com fallback ao cache, para a carteira e os dados abrirem offline.
  - NUNCA cachear /api/auth/*, métodos diferentes de GET, nem respostas com erro.
  - página offline.html amigável quando não houver rede nem cache.
  - fluxo de atualização: ao detectar nova versão, mostrar um aviso "Nova versão disponível — Atualizar" que ativa o novo service worker.
- Botão "Instalar app" usando o evento beforeinstallprompt (Android/Chrome) e, no iOS (que não dispara o evento), um banner com a instrução "Compartilhar > Adicionar à Tela de Início", exibido uma vez e dispensável.
- Indicador discreto de "sem conexão" quando offline.
- Chamados criados offline entram em fila (IndexedDB) e são enviados ao reconectar.
- Servir sw.js e manifest com Content-Type correto e Cache-Control: no-cache; assets com hash/versão podem ter cache longo.

## SERVIDOR E DEPLOY
- main.py monta static/ na raiz, com fallback de SPA para index.html (sem engolir rotas /api e /docs).
- Variáveis de ambiente (.env.example): SECRET_KEY, DATABASE_URL, ACCESS_TOKEN_MINUTES, REFRESH_TOKEN_DAYS, ALLOWED_ORIGINS, SEED_ON_START, ENV.
- Dockerfile enxuto e comando "uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers".
- README.md em português com: como rodar local (venv, pip install, uvicorn), como testar no celular (túnel HTTPS), como publicar em hospedagem gratuita, aviso sobre disco efêmero do SQLite, e uma seção "Migrar para VPS/Hostinger e Postgres" (gunicorn + uvicorn workers, nginx, systemd, DATABASE_URL), além de como usar o CLI e as credenciais de demonstração.

## TESTES E CRITÉRIOS DE ACEITE
- pytest com TestClient: login válido/inválido, rota /api/me protegida, isolamento entre alunos, criação de chamado, refresh token.
- Critérios: o Lighthouse reconhece o app como instalável; abre offline com o app shell e os últimos dados; instala no Android e no iOS; sem erros no console; textos em pt-BR sem cortes em 390 px.

## REGRAS
- Código organizado, tipado e comentado em português.
- Se algo não couber em uma resposta, entregue por partes na ordem: (1) backend + banco + seed, (2) front com api.js, (3) PWA (manifest, sw, ícones), (4) README e testes, e pergunte antes de seguir para a próxima.
- Ao final, liste os arquivos gerados e os comandos para rodar.