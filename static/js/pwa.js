/**
 * PWA: registro do SW, instalar app, banner iOS, offline e atualização.
 */
(function (global) {
  "use strict";

  const IOS_BANNER_KEY = "uniapp_ios_banner_dismissed";
  let deferredPrompt = null;

  function $(id) {
    return document.getElementById(id);
  }

  function isIos() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent);
  }

  function isStandalone() {
    return (
      window.matchMedia("(display-mode: standalone)").matches ||
      // iOS Safari
      navigator.standalone === true
    );
  }

  function setOffline(on) {
    const el = $("offlineBar");
    if (!el) return;
    el.hidden = !on;
    el.setAttribute("aria-hidden", on ? "false" : "true");
  }

  function showUpdateBar() {
    const el = $("updateBar");
    if (!el) return;
    el.hidden = false;
  }

  function hideUpdateBar() {
    const el = $("updateBar");
    if (!el) return;
    el.hidden = true;
  }

  function showInstallBtn(show) {
    const btn = $("btnInstalar");
    if (!btn) return;
    btn.hidden = !show;
  }

  function showIosBanner(show) {
    const el = $("iosBanner");
    if (!el) return;
    el.hidden = !show;
  }

  async function registerSw() {
    if (!("serviceWorker" in navigator)) return null;
    try {
      const reg = await navigator.serviceWorker.register("/sw.js", { scope: "/" });
      if (reg.waiting) showUpdateBar();
      reg.addEventListener("updatefound", () => {
        const worker = reg.installing;
        if (!worker) return;
        worker.addEventListener("statechange", () => {
          if (worker.state === "installed" && navigator.serviceWorker.controller) {
            showUpdateBar();
          }
        });
      });
      return reg;
    } catch (err) {
      console.warn("Falha ao registrar service worker", err);
      return null;
    }
  }

  function bindUpdate() {
    const btn = $("btnAtualizar");
    if (!btn) return;
    btn.addEventListener("click", async () => {
      const reg = await navigator.serviceWorker.getRegistration();
      if (reg && reg.waiting) {
        reg.waiting.postMessage({ type: "SKIP_WAITING" });
      }
      hideUpdateBar();
    });
    navigator.serviceWorker.addEventListener("controllerchange", () => {
      window.location.reload();
    });
  }

  function bindInstall() {
    window.addEventListener("beforeinstallprompt", (e) => {
      e.preventDefault();
      deferredPrompt = e;
      if (!isStandalone()) showInstallBtn(true);
    });

    const btn = $("btnInstalar");
    if (btn) {
      btn.addEventListener("click", async () => {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        await deferredPrompt.userChoice;
        deferredPrompt = null;
        showInstallBtn(false);
      });
    }

    window.addEventListener("appinstalled", () => {
      deferredPrompt = null;
      showInstallBtn(false);
      showIosBanner(false);
    });

    // iOS: instrução manual, uma vez, dispensável
    if (isIos() && !isStandalone() && !localStorage.getItem(IOS_BANNER_KEY)) {
      showIosBanner(true);
    }
    const dismiss = $("btnIosDismiss");
    if (dismiss) {
      dismiss.addEventListener("click", () => {
        localStorage.setItem(IOS_BANNER_KEY, "1");
        showIosBanner(false);
      });
    }
  }

  function bindOffline() {
    setOffline(!navigator.onLine);
    window.addEventListener("online", () => {
      setOffline(false);
      if (typeof global.UniAppFlushQueue === "function") {
        global.UniAppFlushQueue();
      }
    });
    window.addEventListener("offline", () => setOffline(true));
  }

  /* ---- IndexedDB: fila de chamados offline ---- */
  const DB_NAME = "uniapp-offline";
  const STORE = "chamados";

  function openDb() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(STORE)) {
          db.createObjectStore(STORE, { keyPath: "localId", autoIncrement: true });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function enqueueChamado(payload) {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, "readwrite");
      const item = {
        ...payload,
        createdAt: new Date().toISOString(),
        pending: true,
      };
      const req = tx.objectStore(STORE).add(item);
      req.onsuccess = () => resolve({ ...item, localId: req.result, protocolo: "OFF-" + req.result });
      req.onerror = () => reject(req.error);
    });
  }

  async function listPendingChamados() {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, "readonly");
      const req = tx.objectStore(STORE).getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  async function removePending(localId) {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, "readwrite");
      const req = tx.objectStore(STORE).delete(localId);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  async function clearPendingAll() {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, "readwrite");
      const req = tx.objectStore(STORE).clear();
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  global.UniOfflineQueue = {
    enqueueChamado,
    listPendingChamados,
    removePending,
    clearPendingAll,
  };

  document.addEventListener("DOMContentLoaded", () => {
    bindOffline();
    bindInstall();
    bindUpdate();
    registerSw();
  });
})(window);
