"""Smoke da Fase 2: static + login API (via httpx)."""

from __future__ import annotations

import httpx

BASE = "http://127.0.0.1:8000"


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=20.0, follow_redirects=True) as c:
        r = c.get("/")
        assert r.status_code == 200, r.status_code
        assert "screen-login" in r.text
        assert "/js/api.js" in r.text
        assert "screen-biometria" not in r.text
        print("index ok")

        for path in ("/css/app.css", "/js/api.js", "/js/app.js"):
            r = c.get(path)
            assert r.status_code == 200, path
            print(path, "ok", len(r.content))

        r = c.post("/api/auth/login", json={"matricula": "A000001", "senha": "demo1234"})
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}
        r = c.get("/api/me", headers=h)
        assert r.status_code == 200
        assert r.json()["matricula"] == "A000001"
        print("api me ok")
        print("OK")


if __name__ == "__main__":
    main()
