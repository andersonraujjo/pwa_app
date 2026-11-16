/* UniApp service worker — cache versionado */
const SHELL_CACHE = "uniapp-shell-v1";
const API_CACHE = "uniapp-api-v1";

const PRECACHE = [
  "/",
  "/index.html",
  "/offline.html",
  "/css/app.css",
  "/js/api.js",
  "/js/app.js",
  "/js/pwa.js",
  "/manifest.webmanifest",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/icons/maskable-512.png",
  "/icons/apple-touch-icon.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((k) => k.startsWith("uniapp-") && k !== SHELL_CACHE && k !== API_CACHE)
          .map((k) => caches.delete(k))
      );
      await self.clients.claim();
    })()
  );
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

function isAuthApi(url) {
  return url.pathname.startsWith("/api/auth/");
}

function isMeApi(url) {
  return url.pathname.startsWith("/api/me");
}

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const res = await fetch(request);
    if (res.ok) {
      const cache = await caches.open(SHELL_CACHE);
      cache.put(request, res.clone());
    }
    return res;
  } catch (_err) {
    if (request.mode === "navigate") {
      const offline = await caches.match("/offline.html");
      if (offline) return offline;
    }
    throw _err;
  }
}

async function networkFirstApi(request) {
  const cache = await caches.open(API_CACHE);
  try {
    const res = await fetch(request);
    // Nunca cachear erro nem métodos != GET (já filtrado)
    if (res.ok) {
      cache.put(request, res.clone());
    }
    return res;
  } catch (_err) {
    const cached = await cache.match(request);
    if (cached) return cached;
    throw _err;
  }
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  if (url.origin !== self.location.origin) return;

  // Nunca interceptar/cachear auth
  if (isAuthApi(url)) return;

  // Só GET entra em estratégia de cache
  if (request.method !== "GET") return;

  if (isMeApi(url)) {
    event.respondWith(networkFirstApi(request));
    return;
  }

  // App shell e estáticos
  if (
    request.mode === "navigate" ||
    PRECACHE.includes(url.pathname) ||
    url.pathname.startsWith("/css/") ||
    url.pathname.startsWith("/js/") ||
    url.pathname.startsWith("/icons/") ||
    url.pathname === "/manifest.webmanifest"
  ) {
    event.respondWith(cacheFirst(request));
  }
});
