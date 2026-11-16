/**
 * Wrapper de fetch do UniApp.
 * - Anexa Bearer
 * - Renova access via refresh em 401 (uma tentativa)
 * - Aciona o overlay CARREGANDO...
 * - Trata erros de rede
 */
(function (global) {
  "use strict";

  const ACCESS_KEY = "uniapp_access";
  const REFRESH_KEY = "uniapp_refresh";

  let loadingCount = 0;
  let refreshPromise = null;

  function loaderEl() {
    return document.getElementById("loader");
  }

  function setLoading(on) {
    const el = loaderEl();
    if (!el) return;
    if (on) {
      loadingCount += 1;
      el.classList.add("show");
      el.setAttribute("aria-hidden", "false");
    } else {
      loadingCount = Math.max(0, loadingCount - 1);
      if (loadingCount === 0) {
        el.classList.remove("show");
        el.setAttribute("aria-hidden", "true");
      }
    }
  }

  function getAccess() {
    return localStorage.getItem(ACCESS_KEY) || "";
  }

  function getRefresh() {
    return localStorage.getItem(REFRESH_KEY) || "";
  }

  function setTokens(access, refresh) {
    if (access) localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  }

  function clearTokens() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }

  /** Apaga só caches de dados privados (/api/me). Mantém o app shell. */
  async function limparCachesPrivados() {
    if (!("caches" in global)) return;
    try {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((k) => k.startsWith("uniapp-api"))
          .map((k) => caches.delete(k))
      );
    } catch (_err) {
      /* silencioso: logout não deve falhar por cache */
    }
  }

  class ApiError extends Error {
    constructor(message, { status = 0, data = null, network = false } = {}) {
      super(message);
      this.name = "ApiError";
      this.status = status;
      this.data = data;
      this.network = network;
    }
  }

  async function parseBody(res) {
    const ctype = res.headers.get("content-type") || "";
    if (ctype.includes("application/json")) {
      try {
        return await res.json();
      } catch (_e) {
        return null;
      }
    }
    if (ctype.includes("application/pdf") || ctype.includes("octet-stream")) {
      return await res.blob();
    }
    try {
      return await res.text();
    } catch (_e) {
      return null;
    }
  }

  async function rawFetch(path, options = {}, { auth = true, retry = true } = {}) {
    const headers = new Headers(options.headers || {});
    if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    if (auth) {
      const token = getAccess();
      if (token) headers.set("Authorization", `Bearer ${token}`);
    }

    let res;
    try {
      res = await fetch(path, { ...options, headers });
    } catch (_err) {
      throw new ApiError("Sem conexão. Verifique a internet e tente novamente.", {
        network: true,
      });
    }

    if (res.status === 401 && auth && retry) {
      const ok = await tentarRefresh();
      if (ok) return rawFetch(path, options, { auth: true, retry: false });
      clearTokens();
      throw new ApiError("Sessão expirada. Faça login novamente.", { status: 401 });
    }

    const data = await parseBody(res);
    if (!res.ok) {
      const detail =
        (data && (data.detail || data.message)) ||
        `Erro ${res.status}`;
      const msg = typeof detail === "string" ? detail : "Não foi possível concluir a solicitação.";
      throw new ApiError(msg, { status: res.status, data });
    }
    return data;
  }

  async function tentarRefresh() {
    const refresh = getRefresh();
    if (!refresh) return false;
    if (refreshPromise) return refreshPromise;

    refreshPromise = (async () => {
      try {
        const data = await rawFetch(
          "/api/auth/refresh",
          {
            method: "POST",
            body: JSON.stringify({ refresh_token: refresh }),
          },
          { auth: false, retry: false }
        );
        setTokens(data.access_token, data.refresh_token);
        return true;
      } catch (_err) {
        clearTokens();
        return false;
      } finally {
        refreshPromise = null;
      }
    })();

    return refreshPromise;
  }

  async function request(path, options = {}, cfg = {}) {
    const showLoader = cfg.loader !== false;
    if (showLoader) setLoading(true);
    try {
      return await rawFetch(path, options, cfg);
    } finally {
      if (showLoader) setLoading(false);
    }
  }

  const api = {
    ApiError,
    getAccess,
    getRefresh,
    setTokens,
    clearTokens,
    limparCachesPrivados,
    setLoading,
    hasSession() {
      return Boolean(getRefresh() || getAccess());
    },
    async login(matricula, senha) {
      const data = await request(
        "/api/auth/login",
        {
          method: "POST",
          body: JSON.stringify({ matricula, senha }),
        },
        { auth: false }
      );
      // Evita misturar cache de /api/me de outro aluno neste aparelho
      await limparCachesPrivados();
      setTokens(data.access_token, data.refresh_token);
      return data;
    },
    async logout() {
      const refresh = getRefresh();
      try {
        if (refresh) {
          await request(
            "/api/auth/logout",
            {
              method: "POST",
              body: JSON.stringify({ refresh_token: refresh }),
            },
            { auth: false, loader: false }
          );
        }
      } catch (_err) {
        /* mesmo com falha de rede, limpa localmente */
      }
      clearTokens();
      await limparCachesPrivados();
    },
    me(opts) {
      return request("/api/me", {}, opts);
    },
    carteira(opts) {
      return request("/api/me/carteira", {}, opts);
    },
    pagamentos(opts) {
      return request("/api/me/pagamentos", {}, opts);
    },
    disciplinas(semestre, opts) {
      return request(`/api/me/disciplinas?semestre=${encodeURIComponent(semestre)}`, {}, opts);
    },
    notas(opts) {
      return request("/api/me/notas", {}, opts);
    },
    atestado(opts) {
      return request("/api/me/atestado", {}, opts);
    },
    chamados(opts) {
      return request("/api/me/chamados", {}, opts);
    },
    criarChamado(payload, opts) {
      return request(
        "/api/me/chamados",
        { method: "POST", body: JSON.stringify(payload) },
        opts
      );
    },
    chamado(id, opts) {
      return request(`/api/me/chamados/${encodeURIComponent(id)}`, {}, opts);
    },
  };

  global.UniApi = api;
})(window);
