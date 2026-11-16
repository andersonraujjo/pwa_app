"""Smoke Fase 3: manifest, SW, ícones, offline page."""

from __future__ import annotations

import httpx

BASE = "http://127.0.0.1:8000"


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=20.0) as c:
        r = c.get("/")
        assert r.status_code == 200
        assert 'rel="manifest"' in r.text
        assert "/js/pwa.js" in r.text
        assert "apple-mobile-web-app-capable" in r.text
        print("index metas ok")

        r = c.get("/manifest.webmanifest")
        assert r.status_code == 200
        assert "application/manifest+json" in r.headers.get("content-type", "")
        assert r.headers.get("cache-control", "").lower().find("no-cache") >= 0
        body = r.json()
        assert body["short_name"] == "UniApp"
        assert body["display"] == "standalone"
        print("manifest ok")

        r = c.get("/sw.js")
        assert r.status_code == 200
        assert "javascript" in r.headers.get("content-type", "")
        assert "uniapp-shell-v1" in r.text
        assert r.headers.get("cache-control", "").lower().find("no-cache") >= 0
        print("sw ok")

        r = c.get("/offline.html")
        assert r.status_code == 200
        assert "offline" in r.text.lower()
        print("offline page ok")

        for path in (
            "/icons/icon-192.png",
            "/icons/icon-512.png",
            "/icons/maskable-512.png",
            "/icons/apple-touch-icon.png",
            "/js/pwa.js",
        ):
            r = c.get(path)
            assert r.status_code == 200, path
            print(path, "ok")

        print("OK")


if __name__ == "__main__":
    main()
