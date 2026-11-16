/**
 * UniApp — front do portal do aluno.
 * Visual preservado do protótipo; dados vêm da API.
 * TODO fase 2: WebAuthn (substituir/complementar login por biometria real).
 */
(function () {
  "use strict";

  const api = window.UniApi;

  const statusLabel = {
    aberto: "Aberto",
    andamento: "Em andamento",
    resolvido: "Resolvido",
  };
  const urgLabel = { baixa: "Baixa", media: "Média", alta: "Alta" };

  const atalhos = [
    { label: "Pagamentos", icon: "card", tela: "pagamentos" },
    { label: "Meus Dados", icon: "user", tela: "dados" },
    { label: "Carteira Estudantil", icon: "id", tela: "carteira" },
    { label: "Posição Financeira", icon: "chart" },
    { label: "Atestado de Matrícula", icon: "doc", tela: "atestado", share: true },
    { label: "Extrato", icon: "list" },
    { label: "Histórico Escolar", icon: "history" },
    { label: "Notas e Faltas", icon: "clipboard", tela: "notas" },
    { label: "Médias e Exames", icon: "percent" },
    { label: "Integralização Curricular", icon: "grid", tela: "integralizacao" },
    { label: "AVA", icon: "monitor" },
    { label: "Disciplinas Online", icon: "play" },
    { label: "Trabalhos Acadêmicos", icon: "pencil" },
    { label: "Atividades Complementares", icon: "star" },
    { label: "Minha Biblioteca", icon: "book" },
    { label: "Biblioteca Virtual", icon: "globe" },
    { label: "Iniciação Científica", icon: "flask" },
    { label: "Documentos de Estágio", icon: "case" },
    { label: "Chamados", icon: "ticket", tela: "chamados", novo: true },
  ];

  const iconPaths = {
    card: '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18"/>',
    user: '<circle cx="12" cy="8" r="3.2"/><path d="M5.5 19c.8-3.3 3.3-5 6.5-5s5.7 1.7 6.5 5"/>',
    id: '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="12" r="2"/><path d="M13 10h5M13 14h4"/>',
    chart: '<path d="M4 19V5M4 19h16"/><path d="M8 15l3.2-3.8L14 14l4-5"/>',
    doc: '<path d="M7 3.5h7l4.5 4.5V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1z"/><path d="M14 3.5V8h4.5M8 13h8M8 17h5"/>',
    list: '<path d="M4 7h2M4 12h2M4 17h2M9 7h11M9 12h11M9 17h11"/>',
    history: '<circle cx="12" cy="12" r="8"/><path d="M12 8v4.5l3 2"/>',
    clipboard: '<rect x="7" y="4" width="10" height="16" rx="2"/><path d="M9 4.2h6V7H9zM9 11h6M9 15h4"/>',
    percent: '<path d="M18 6L6 18"/><circle cx="8" cy="8" r="2.1"/><circle cx="16" cy="16" r="2.1"/>',
    grid: '<rect x="4" y="4" width="6.5" height="6.5" rx="1.4"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1.4"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1.4"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.4"/>',
    monitor: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    play: '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M10 9l6 3-6 3V9z"/>',
    pencil: '<path d="M4 20l1.2-4.2L16.5 4.5l3 3L8.2 18.8 4 20z"/><path d="M14.2 6.8l3 3"/>',
    star: '<path d="M12 3.5l2.2 4.6 5 .7-3.6 3.5.9 5.1L12 15.8 7.5 17.4l.9-5.1L4.8 8.8l5-.7L12 3.5z"/>',
    book: '<path d="M5 5.5A2.5 2.5 0 0 1 7.5 4H19v15H7.5A2.5 2.5 0 0 0 5 21.5V5.5z"/>',
    globe: '<circle cx="12" cy="12" r="8"/><path d="M4 12h16"/><path d="M12 4c2.2 2.3 3.3 5 3.3 8s-1.1 5.7-3.3 8c-2.2-2.3-3.3-5-3.3-8s1.1-5.7 3.3-8z"/>',
    flask: '<path d="M9 3h6M10 3v5.2L5.6 18a2 2 0 0 0 1.7 3h9.4a2 2 0 0 0 1.7-3L14 8.2V3"/><path d="M8.2 14h7.6"/>',
    case: '<rect x="3" y="7" width="18" height="12" rx="2"/><path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h5A1.5 1.5 0 0 1 16 5.5V7M3 12h18"/>',
    ticket: '<path d="M5 7h14a1 1 0 0 1 1 1v3a2 2 0 0 0 0 4v3a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-3a2 2 0 0 0 0-4V8a1 1 0 0 1 1-1z"/><path d="M12 8v8"/>',
  };

  let current = "splash";
  let stack = ["splash"];
  let busy = false;
  let openShareOnEnter = false;
  let carteiraOffline = false;
  let toastTimer = 0;
  let meCache = null;
  let chamadosCache = [];
  let atestadoUrl = null;
  const overlays = [];

  function esc(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function svg(inner) {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${inner}</svg>`;
  }

  function fmtNota(n) {
    if (n === null || n === undefined) return "—";
    return Number(n).toFixed(1).replace(".", ",");
  }

  function fmtMoney(n) {
    return Number(n).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  }

  function fmtDate(iso) {
    if (!iso) return "—";
    const s = String(iso).slice(0, 10);
    const [y, m, d] = s.split("-");
    if (!y || !m || !d) return String(iso);
    return `${d}/${m}/${y}`;
  }

  function fmtDateTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return String(iso);
    const p = (n) => String(n).padStart(2, "0");
    return `${p(d.getDate())}/${p(d.getMonth() + 1)}/${d.getFullYear()}`;
  }

  function toast(msg) {
    const el = document.getElementById("toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), 1800);
  }

  function openOverlay(id) {
    const el = document.getElementById(id);
    el.hidden = false;
    if (!overlays.includes(id)) overlays.push(id);
  }

  function closeOverlay(id) {
    const target = id || overlays[overlays.length - 1];
    if (!target) return;
    const el = document.getElementById(target);
    if (el) el.hidden = true;
    const idx = overlays.lastIndexOf(target);
    if (idx >= 0) overlays.splice(idx, 1);
  }

  function closeAllOverlays() {
    overlays.splice(0).forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.hidden = true;
    });
  }

  function navigate(id, opts) {
    const options = opts || {};
    if (busy) return;
    if (id === current && !options.force) return;
    busy = true;
    if (options.share) openShareOnEnter = true;
    api.setLoading(true);
    setTimeout(() => {
      closeAllOverlays();
      if (options.reset) stack = [id];
      else stack.push(id);
      setScreen(id, options.dir || "forward");
      api.setLoading(false);
      busy = false;
    }, 600);
  }

  function goBack() {
    if (busy || stack.length < 2) return;
    busy = true;
    api.setLoading(true);
    setTimeout(() => {
      closeAllOverlays();
      stack.pop();
      setScreen(stack[stack.length - 1], "back");
      api.setLoading(false);
      busy = false;
    }, 600);
  }

  function setScreen(id, dir) {
    const next = document.getElementById("screen-" + id);
    document.querySelectorAll(".screen").forEach((s) => {
      if (s !== next) {
        s.classList.remove("active", "from-left", "from-right");
        s.setAttribute("aria-hidden", "true");
      }
    });
    next.setAttribute("aria-hidden", "false");
    next.classList.remove("from-left", "from-right", "active");
    void next.offsetWidth;
    next.classList.add("active");
    if (dir) next.classList.add(dir === "back" ? "from-left" : "from-right");
    current = id;

    if (id === "home") enterHome();
    if (id === "carteira") enterCarteira();
    if (id === "dados") enterDados();
    if (id === "pagamentos") enterPagamentos();
    if (id === "atestado") enterAtestado();
    if (id === "integralizacao") enterIntegralizacao();
    if (id === "notas") enterNotas();
    if (id === "chamados") enterChamados();
    if (id === "login") resetLoginForm();
  }

  function renderAtalhos() {
    document.getElementById("gridAtalhos").innerHTML = atalhos
      .map((a) => {
        const action = a.tela ? "go" : "soon";
        const tela = a.tela ? ` data-tela="${a.tela}"` : "";
        const share = a.share ? ' data-share="1"' : "";
        const selo = a.novo ? '<span class="selo">novo</span>' : "";
        return `<button type="button" class="atalho" data-action="${action}"${tela}${share}>${selo}<span class="ico">${svg(iconPaths[a.icon])}</span><span class="lbl">${esc(a.label)}</span></button>`;
      })
      .join("");
  }

  async function ensureMe() {
    if (meCache) return meCache;
    meCache = await api.me();
    return meCache;
  }

  async function enterHome() {
    try {
      const me = await ensureMe();
      const primeiro = (me.nome || "Aluno").split(/\s+/)[0];
      document.querySelector("#screen-home .hello").textContent = `Olá, ${primeiro}`;
      document.getElementById("homeCurso").textContent = me.curso.nome;
      document.getElementById("homeMat").textContent = me.matricula;
      const chipStatus = document.querySelector("#screen-home .chip-green");
      if (chipStatus) chipStatus.textContent = me.status || "Ativo";
    } catch (err) {
      toast(err.message || "Erro ao carregar perfil");
      if (err.status === 401) forceLogin();
    }
  }

  async function enterCarteira() {
    try {
      const data = await api.carteira();
      document.getElementById("cardNome").textContent = data.nome;
      document.getElementById("cardCurso").textContent = data.curso;
      document.getElementById("cardMat").textContent = data.matricula;
      document.getElementById("cardTurma").textContent = data.turma;
      document.getElementById("cardCampus").textContent = data.campus;
      document.getElementById("cardVal").textContent = data.validade_carteira;
      document.getElementById("progressValue").textContent = data.progresso_percentual + "%";
      document.getElementById("progressBar").style.width = data.progresso_percentual + "%";
      document.getElementById("geradoEm").textContent = "Gerado em " + data.gerado_em;
      document.getElementById("qrHost").innerHTML = data.qr_svg;
      const statusChip = document.querySelector("#screen-carteira .id-chips .chip-green");
      if (statusChip) statusChip.textContent = data.status || "Ativo";
      syncOfflineUi();
    } catch (err) {
      toast(err.message || "Erro ao carregar carteira");
    }
  }

  function syncOfflineUi() {
    const btn = document.getElementById("offlineBtn");
    btn.setAttribute("aria-pressed", carteiraOffline ? "true" : "false");
    document.getElementById("offlineFlag").hidden = !carteiraOffline;
    document.getElementById("offlineText").textContent = carteiraOffline
      ? "Carteirinha disponível sem internet neste aparelho."
      : "Ative para abrir a carteirinha sem internet.";
  }

  function field(label, value, wide) {
    return `<div class="field${wide ? " span-2" : ""}"><small>${esc(label)}</small><span class="value">${esc(value)}</span></div>`;
  }

  async function enterDados() {
    try {
      const a = await ensureMe();
      const avatar =
        '<svg class="avatar" viewBox="0 0 80 80" width="64" height="64" aria-hidden="true"><circle cx="40" cy="40" r="40" fill="#D9E0F7"/><circle cx="40" cy="32" r="12" fill="#12208F"/><path d="M14 68c5-16 16-22 26-22s21 6 26 22" fill="#12208F"/></svg>';
      document.getElementById("dadosConteudo").innerHTML = `
        <article class="card profile">${avatar}<div><h2>${esc(a.nome)}</h2><p>${esc(a.curso.nome)}</p><span class="chip chip-green">${esc(a.status)}</span></div></article>
        <h2 class="sec-title">Dados acadêmicos</h2>
        <section class="card"><div class="fields">
          ${field("Matrícula", a.matricula)}
          ${field("Turma", a.turma)}
          ${field("Código do curso", a.curso.codigo)}
          ${field("Ano/grade", a.ano_grade)}
          ${field("Ingresso", a.ingresso)}
          ${field("Ano letivo", a.ano_letivo)}
          ${field("Nome do curso", a.curso.nome, true)}
          ${field("Unidade", a.unidade, true)}
        </div></section>
        <h2 class="sec-title">Dados pessoais</h2>
        <section class="card"><div class="fields">
          ${field("Sexo", a.sexo)}
          ${field("Nascimento", a.nascimento)}
          ${field("CPF", a.cpf)}
          ${field("RG", a.rg)}
          ${field("Telefone", a.telefone)}
          ${field("Ingresso", a.ingresso)}
          ${field("E-mail", a.email, true)}
        </div></section>
        <h2 class="sec-title">Endereço</h2>
        <section class="card"><div class="fields">
          ${field("Logradouro", a.logradouro, true)}
          ${field("Complemento", a.complemento || "—")}
          ${field("Bairro", a.bairro)}
          ${field("CEP", a.cep)}
          ${field("Cidade/UF", a.cidade_uf, true)}
        </div></section>`;
    } catch (err) {
      toast(err.message || "Erro ao carregar dados");
    }
  }

  async function enterPagamentos() {
    const host = document.getElementById("pagamentosLista");
    try {
      const itens = await api.pagamentos();
      if (!itens.length) {
        host.innerHTML = '<p class="empty">Nenhuma parcela em aberto.</p>';
        return;
      }
      host.innerHTML = itens
        .map((p) => {
          const statusChip =
            String(p.status).toUpperCase().includes("ABERTO")
              ? "chip-amber"
              : "chip-green";
          return `<article class="card">
            <div class="pay-head">
              <div>
                <small class="pay-label">Mensalidade</small>
                <h2>${esc(p.referencia)}</h2>
              </div>
              <span class="chip ${statusChip}">${esc(p.status)}</span>
            </div>
            <div style="margin-top:12px;">
              <small class="pay-label">Valor do documento</small>
              <p class="money-muted">${esc(fmtMoney(p.valor_documento))}</p>
            </div>
            <div style="margin-top:10px;">
              <small class="pay-label">Valor a pagar</small>
              <p class="money-amber">${esc(fmtMoney(p.valor_pagar))}</p>
            </div>
            <div class="pay-grid">
              <div><small class="pay-label">Vencimento</small><span class="value">${esc(fmtDate(p.vencimento))}</span></div>
              <div><small class="pay-label">Prazo de antecipação</small><span class="value">${esc(fmtDate(p.antecipacao_ate))}</span></div>
            </div>
            <div class="pay-actions">
              <button type="button" class="btn btn-navy" data-action="pay" data-metodo="pix" data-valor="${esc(fmtMoney(p.valor_pagar))}">Pix</button>
              <button type="button" class="btn btn-navy" data-action="pay" data-metodo="boleto" data-valor="${esc(fmtMoney(p.valor_pagar))}">Boleto</button>
              <button type="button" class="btn btn-navy" data-action="pay" data-metodo="cartao" data-valor="${esc(fmtMoney(p.valor_pagar))}">Cartão</button>
            </div>
          </article>`;
        })
        .join("");
    } catch (err) {
      host.innerHTML = `<p class="empty">${esc(err.message || "Erro ao carregar pagamentos")}</p>`;
    }
  }

  async function enterAtestado() {
    if (atestadoUrl) {
      URL.revokeObjectURL(atestadoUrl);
      atestadoUrl = null;
    }
    try {
      const blob = await api.atestado();
      atestadoUrl = URL.createObjectURL(blob);
      document.getElementById("atestadoMeta").textContent =
        "PDF · " + Math.max(1, Math.round(blob.size / 1024)) + " KB";
      if (openShareOnEnter) {
        openShareOnEnter = false;
        openOverlay("overlayShare");
      }
    } catch (err) {
      toast(err.message || "Erro ao gerar atestado");
    }
  }

  async function enterIntegralizacao(semestre) {
    const sem = semestre || Number(document.querySelector("#tabsSem .on")?.dataset.sem || 1);
    document.querySelectorAll("#tabsSem [data-sem]").forEach((btn) => {
      const on = Number(btn.dataset.sem) === Number(sem);
      btn.classList.toggle("on", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    const host = document.getElementById("semPanels");
    try {
      const discs = await api.disciplinas(sem);
      if (!discs.length) {
        host.innerHTML = '<p class="empty">Nenhuma disciplina neste semestre.</p>';
        return;
      }
      host.innerHTML = discs
        .map((d) => {
          const mediaLabel = d.status === "CURSANDO" ? "Média parcial" : "Média final";
          const stClass = d.status === "APROVADO" ? "st-ok" : "st-warn";
          return `<article class="disc">
            <div class="disc-top"><strong>${esc(d.codigo)}</strong><span>${esc(d.nome)}</span></div>
            <div class="disc-grid">
              <div><small>Carga horária</small><span class="value">${d.carga_horaria} h</span></div>
              <div><small>Ano/grade</small><span class="value">${esc(d.ano_grade)}</span></div>
              <div><small>Status</small><span class="value ${stClass}">${esc(d.status)}</span></div>
              <div><small>${mediaLabel}</small><span class="nota-destaque">${fmtNota(d.media_final)}</span></div>
            </div>
          </article>`;
        })
        .join("");
    } catch (err) {
      host.innerHTML = `<p class="empty">${esc(err.message || "Erro ao carregar disciplinas")}</p>`;
    }
  }

  async function enterNotas() {
    const host = document.getElementById("listaNotas");
    try {
      const lista = await api.notas();
      host.innerHTML = lista
        .map((d, i) => {
          const baixa = d.frequencia < 75;
          const bins = (d.notas || [])
            .map(
              (n, idx) =>
                `<div><small>${idx + 1}º bimestre</small><span class="value">${fmtNota(n)}</span></div>`
            )
            .join("");
          return `<article class="acc">
            <button type="button" class="acc-btn" data-action="acc" aria-expanded="false" aria-controls="acc-${i}">
              ${baixa ? '<span class="dot-alert" aria-hidden="true"></span>' : ""}
              <span class="txt"><b>${esc(d.nome)}</b><small>${esc(d.codigo)} · ${esc(d.status)}</small></span>
              <span class="acc-media">${fmtNota(d.media)}</span>
              <svg class="chev" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>
            </button>
            <div class="acc-panel" id="acc-${i}">
              <div class="bimestres">${bins}
                <div><small>Média</small><span class="value">${fmtNota(d.media)}</span></div>
                <div><small>Faltas</small><span class="value">${d.faltas}</span></div>
              </div>
              <div class="freq">
                <div class="row"><span>Frequência</span><b>${d.frequencia}%</b></div>
                <div class="bar track"><span style="width:${d.frequencia}%;background:${baixa ? "#F5A623" : "#1DB954"}"></span></div>
              </div>
              ${baixa ? '<div class="alert">Frequência abaixo de 75%</div>' : ""}
            </div>
          </article>`;
        })
        .join("");
    } catch (err) {
      host.innerHTML = `<p class="empty">${esc(err.message || "Erro ao carregar notas")}</p>`;
    }
  }

  function renderChamadosLista() {
    const host = document.getElementById("listaChamados");
    if (!chamadosCache.length) {
      host.innerHTML = '<p class="empty">Nenhum chamado ainda.</p>';
      return;
    }
    host.innerHTML = chamadosCache
      .map((c) => {
        const pending = Boolean(c.pending || c.localId);
        const st = pending ? "pendente" : c.status || "aberto";
        const label = pending ? "Na fila" : statusLabel[st] || st;
        const chip = pending ? "chip-pendente" : `chip-${esc(st)}`;
        const action = pending
          ? `data-action="chamado-local" data-local="${c.localId}"`
          : `data-action="chamado" data-id="${c.id}"`;
        return `<button type="button" class="ticket" ${action}>
          <span class="ticket-top"><strong>${esc(c.protocolo)}</strong><span class="chip ${chip}">${esc(label)}</span></span>
          <span class="ticket-tipo">${esc(c.tipo)}</span>
          <span class="ticket-meta">${esc(c.setor)} · ${esc(fmtDateTime(c.criado_em || c.createdAt))} · ${esc(urgLabel[c.urgencia] || c.urgencia)}</span>
        </button>`;
      })
      .join("");
  }

  async function mergeChamadosComFila(serverList) {
    let pending = [];
    try {
      if (window.UniOfflineQueue) {
        pending = await window.UniOfflineQueue.listPendingChamados();
      }
    } catch (_err) {
      pending = [];
    }
    const mapped = pending.map((p) => ({
      ...p,
      pending: true,
      status: "pendente",
      criado_em: p.createdAt,
    }));
    chamadosCache = [...mapped, ...(serverList || [])];
  }

  async function enterChamados() {
    try {
      const lista = await api.chamados();
      await mergeChamadosComFila(lista);
      renderChamadosLista();
    } catch (err) {
      // Offline: tenta só a fila + cache vazio
      try {
        await mergeChamadosComFila([]);
        if (chamadosCache.length) {
          renderChamadosLista();
          toast("Exibindo chamados da fila offline");
          return;
        }
      } catch (_e) {
        /* ignore */
      }
      document.getElementById("listaChamados").innerHTML =
        `<p class="empty">${esc(err.message || "Erro ao carregar chamados")}</p>`;
    }
  }

  async function abrirChamadoLocal(localId) {
    try {
      const pending = await window.UniOfflineQueue.listPendingChamados();
      const c = pending.find((p) => String(p.localId) === String(localId));
      if (!c) {
        toast("Chamado local não encontrado");
        return;
      }
      document.getElementById("tlTitulo").textContent = c.protocolo || "OFF-" + c.localId;
      document.getElementById("tlSub").textContent =
        c.tipo + " · " + fmtDateTime(c.createdAt);
      document.getElementById("tlDesc").textContent = c.descricao;
      document.getElementById("tlLista").innerHTML =
        `<li class="current"><span class="dot"></span><b>Aguardando conexão</b><small>Será enviado ao reconectar</small></li>`;
      openOverlay("overlayTimeline");
    } catch (err) {
      toast(err.message || "Erro ao abrir chamado local");
    }
  }

  async function abrirChamado(id) {
    try {
      const c = await api.chamado(id);
      document.getElementById("tlTitulo").textContent = c.protocolo;
      document.getElementById("tlSub").textContent =
        c.tipo + " · " + fmtDateTime(c.criado_em);
      document.getElementById("tlDesc").textContent = c.descricao;
      const eventos = c.eventos || [];
      document.getElementById("tlLista").innerHTML = eventos
        .map((e, i) => {
          const cls = i === eventos.length - 1 ? "current" : "done";
          return `<li class="${cls}"><span class="dot"></span><b>${esc(e.descricao)}</b><small>${esc(fmtDateTime(e.criado_em))}</small></li>`;
        })
        .join("");
      openOverlay("overlayTimeline");
    } catch (err) {
      toast(err.message || "Erro ao abrir chamado");
    }
  }

  function abrirPagamento(metodo, valor) {
    const title = document.getElementById("payTitle");
    const body = document.getElementById("payBody");
    const btn = document.getElementById("payMain");
    btn.dataset.metodo = metodo;
    const valorHtml = `<p class="pay-label">Valor a pagar</p><p class="money-amber">${esc(valor || "—")}</p>`;
    if (metodo === "pix") {
      title.textContent = "Pix";
      body.innerHTML =
        valorHtml +
        '<p class="hint">Código ilustrativo. Nenhum pagamento é processado.</p><code class="fake-code">00020126EXEMPLO.UNIAPP.ALUNO0000005204000053039865406890.005802BR5913ALUNO EXEMPLO6009EXEMPLO6304ABCD</code>';
      btn.textContent = "Fechar";
    } else if (metodo === "boleto") {
      title.textContent = "Boleto";
      body.innerHTML =
        valorHtml +
        '<p class="hint">Linha digitável fictícia.</p><code class="fake-code">00000.00000 00000.000000 00000.000000 0 00000000000000</code>';
      btn.textContent = "Fechar";
    } else {
      title.textContent = "Cartão";
      body.innerHTML =
        valorHtml +
        '<p class="hint">Simulação de cartão. Nenhum dado é enviado e nenhum valor é cobrado.</p><code class="fake-code">Nome: ALUNO EXEMPLO\n**** **** **** 0000 · 00/00</code>';
      btn.textContent = "Simular pagamento";
    }
    openOverlay("overlayPay");
  }

  function resetLoginForm() {
    const form = document.getElementById("formLogin");
    const erro = document.getElementById("loginErro");
    const btn = document.getElementById("btnLogin");
    if (erro) {
      erro.hidden = true;
      erro.textContent = "";
    }
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Entrar";
    }
    if (form) {
      const senha = form.elements.namedItem("senha");
      if (senha) {
        senha.type = "password";
        document.getElementById("toggleSenha").textContent = "Ver";
      }
    }
  }

  function forceLogin() {
    meCache = null;
    chamadosCache = [];
    stack = ["login"];
    setScreen("login", "forward");
  }

  async function confirmarSaida() {
    closeOverlay("overlaySair");
    try {
      await api.logout();
    } catch (_err) {
      api.clearTokens();
    }
    try {
      if (window.UniOfflineQueue) await window.UniOfflineQueue.clearPendingAll();
    } catch (_e) {
      /* ignore */
    }
    meCache = null;
    chamadosCache = [];
    if (atestadoUrl) {
      URL.revokeObjectURL(atestadoUrl);
      atestadoUrl = null;
    }
    navigate("login", { reset: true });
  }

  async function flushChamadosQueue() {
    if (!window.UniOfflineQueue || !api.hasSession() || !navigator.onLine) return;
    let pending = [];
    try {
      pending = await window.UniOfflineQueue.listPendingChamados();
    } catch (_err) {
      return;
    }
    for (const item of pending) {
      try {
        const criado = await api.criarChamado(
          {
            setor: item.setor,
            tipo: item.tipo,
            urgencia: item.urgencia,
            descricao: item.descricao,
          },
          { loader: false }
        );
        await window.UniOfflineQueue.removePending(item.localId);
        chamadosCache = [
          criado,
          ...chamadosCache.filter(
            (c) => c.localId !== item.localId && c.id !== criado.id
          ),
        ];
      } catch (_err) {
        break;
      }
    }
    if (current === "chamados") renderChamadosLista();
  }

  window.UniAppFlushQueue = flushChamadosQueue;

  document.getElementById("phone").addEventListener("click", (e) => {
    if (e.target.dataset && e.target.dataset.action === "scrim") {
      closeOverlay(e.target.id);
      return;
    }
    const el = e.target.closest("[data-action]");
    if (!el) return;
    const action = el.dataset.action;

    if (action === "back") {
      if (overlays.length) closeOverlay();
      else goBack();
      return;
    }
    if (action === "go") {
      navigate(el.dataset.tela, { share: el.dataset.share === "1" });
      return;
    }
    if (action === "soon") {
      toast("Em breve");
      return;
    }
    if (action === "logout") {
      openOverlay("overlaySair");
      return;
    }
    if (action === "close") {
      closeOverlay();
      return;
    }
    if (action === "confirm-exit") {
      confirmarSaida();
      return;
    }
    if (action === "pay") {
      abrirPagamento(el.dataset.metodo, el.dataset.valor);
      return;
    }
    if (action === "pay-main") {
      if (el.dataset.metodo === "cartao") toast("Pagamento com cartão simulado");
      closeOverlay("overlayPay");
      return;
    }
    if (action === "open-share") {
      openOverlay("overlayShare");
      return;
    }
    if (action === "share") {
      if (atestadoUrl && el.dataset.app === "Salvar em arquivos") {
        const a = document.createElement("a");
        a.href = atestadoUrl;
        a.download = "AtestadoMatricula.pdf";
        a.click();
      }
      toast("Simulação: " + el.dataset.app);
      closeOverlay("overlayShare");
      return;
    }
    if (action === "catraca") {
      toast("Acesso às catracas liberado (simulação)");
      return;
    }
    if (action === "offline") {
      carteiraOffline = !carteiraOffline;
      syncOfflineUi();
      return;
    }
    if (action === "semestre") {
      enterIntegralizacao(el.dataset.sem);
      return;
    }
    if (action === "acc") {
      const item = el.closest(".acc");
      const wasOpen = item.classList.contains("open");
      document.querySelectorAll("#listaNotas .acc").forEach((n) => {
        n.classList.remove("open");
        const b = n.querySelector(".acc-btn");
        if (b) b.setAttribute("aria-expanded", "false");
      });
      if (!wasOpen) {
        item.classList.add("open");
        el.setAttribute("aria-expanded", "true");
      }
      return;
    }
    if (action === "chamado") {
      abrirChamado(el.dataset.id);
      return;
    }
    if (action === "chamado-local") {
      abrirChamadoLocal(el.dataset.local);
      return;
    }
    if (action === "toggle-senha") {
      const input = document.getElementById("loginSenha");
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      el.textContent = show ? "Ocultar" : "Ver";
    }
  });

  document.getElementById("formLogin").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.target;
    const matricula = String(form.matricula.value || "").trim();
    const senha = String(form.senha.value || "");
    const erro = document.getElementById("loginErro");
    const btn = document.getElementById("btnLogin");
    erro.hidden = true;
    erro.textContent = "";
    if (!matricula || !senha) {
      erro.hidden = false;
      erro.textContent = "Informe matrícula e senha.";
      return;
    }
    btn.disabled = true;
    btn.textContent = "Entrando...";
    try {
      await api.login(matricula, senha);
      meCache = null;
      navigate("home", { reset: true });
    } catch (err) {
      erro.hidden = false;
      erro.textContent = err.message || "Não foi possível entrar.";
    } finally {
      btn.disabled = false;
      btn.textContent = "Entrar";
    }
  });

  document.getElementById("formChamado").addEventListener("submit", async (e) => {
    e.preventDefault();
    const dados = new FormData(e.target);
    const descricao = String(dados.get("descricao") || "").trim();
    const erro = document.getElementById("formErro");
    if (descricao.length < 8) {
      erro.hidden = false;
      erro.textContent = "Descreva o problema para enviar o chamado.";
      return;
    }
    erro.hidden = true;
    const payload = {
      setor: String(dados.get("setor")),
      tipo: String(dados.get("tipo")),
      urgencia: document.querySelector('input[name="urgencia"]:checked').value,
      descricao,
    };
    try {
      const criado = await api.criarChamado(payload);
      e.target.reset();
      chamadosCache = [criado, ...chamadosCache.filter((c) => c.id !== criado.id)];
      renderChamadosLista();
      toast("Chamado " + criado.protocolo + " enviado");
      const scroller = document.getElementById("chamadosBody");
      const lista = document.getElementById("listaChamados");
      const top =
        lista.getBoundingClientRect().top -
        scroller.getBoundingClientRect().top +
        scroller.scrollTop;
      scroller.scrollTo({ top: Math.max(0, top - 8), behavior: "smooth" });
    } catch (err) {
      if (err.network || !navigator.onLine) {
        try {
          const local = await window.UniOfflineQueue.enqueueChamado(payload);
          e.target.reset();
          chamadosCache = [
            {
              ...local,
              pending: true,
              status: "pendente",
              criado_em: local.createdAt,
            },
            ...chamadosCache,
          ];
          renderChamadosLista();
          toast("Sem rede — chamado guardado na fila");
          return;
        } catch (_e) {
          /* cai no erro padrão */
        }
      }
      erro.hidden = false;
      erro.textContent = err.message || "Falha ao enviar chamado.";
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (overlays.length) closeOverlay();
    else if (current !== "home" && current !== "splash" && current !== "login") goBack();
  });

  async function boot() {
    renderAtalhos();
    // Splash curto; depois login ou home se já houver sessão
    setTimeout(async () => {
      if (api.hasSession()) {
        try {
          meCache = await api.me({ loader: false });
          navigate("home", { reset: true });
          flushChamadosQueue();
          return;
        } catch (_err) {
          api.clearTokens();
        }
      }
      navigate("login", { reset: true });
    }, 1500);
  }

  boot();
})();
