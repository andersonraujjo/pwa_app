"""Smoke test rápido da Fase 1 (não faz parte da suíte pytest ainda)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    # Context manager dispara o lifespan (create_all + seed)
    with TestClient(app) as client:
        r = client.get("/api/health")
        print("health", r.status_code, r.json())
        assert r.status_code == 200

        r = client.post("/api/auth/login", json={"matricula": "A000001", "senha": "demo1234"})
        print("login", r.status_code)
        assert r.status_code == 200, r.text
        tokens = r.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        r = client.get("/api/me", headers=headers)
        print("me", r.status_code, r.json()["nome"], r.json()["matricula"])
        assert r.json()["nome"] == "Aluno Exemplo"

        r = client.get("/api/me/carteira", headers=headers)
        body = r.json()
        print(
            "carteira",
            r.status_code,
            "svg" in body["qr_svg"].lower(),
            body["progresso_percentual"],
        )
        assert r.status_code == 200
        assert "<svg" in body["qr_svg"].lower()

        r = client.get("/api/me/pagamentos", headers=headers)
        print("pagamentos", r.status_code, len(r.json()), r.json()[0]["referencia"])
        assert r.status_code == 200

        r = client.get("/api/me/disciplinas?semestre=1", headers=headers)
        print("disc1", r.status_code, len(r.json()), r.json()[0]["codigo"])
        assert len(r.json()) == 5

        r = client.get("/api/me/notas", headers=headers)
        notas = r.json()
        baixa = [(n["codigo"], n["frequencia"]) for n in notas if n["frequencia"] < 75]
        print("notas", r.status_code, len(notas), "baixa_freq", baixa)
        assert any(c == "DS402" for c, _ in baixa)

        r = client.get("/api/me/atestado", headers=headers)
        print("atestado", r.status_code, r.headers.get("content-type"), len(r.content))
        assert r.status_code == 200
        assert r.content[:4] == b"%PDF"

        r = client.get("/api/me/chamados", headers=headers)
        print("chamados", r.status_code, len(r.json()))
        assert len(r.json()) >= 3

        r = client.post(
            "/api/me/chamados",
            headers=headers,
            json={
                "setor": "Secretaria",
                "tipo": "Outros",
                "urgencia": "baixa",
                "descricao": "Teste de chamado via API seed fase 1",
            },
        )
        print("criar", r.status_code, r.json()["protocolo"], len(r.json()["eventos"]))
        assert r.status_code == 201
        cid = r.json()["id"]

        r = client.get(f"/api/me/chamados/{cid}", headers=headers)
        print("detalhe", r.status_code, r.json()["protocolo"])
        assert r.status_code == 200

        r2 = client.post("/api/auth/login", json={"matricula": "A000002", "senha": "demo1234"})
        h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}
        r = client.get(f"/api/me/chamados/{cid}", headers=h2)
        print("isolamento", r.status_code)
        assert r.status_code == 404

        r = client.post("/api/auth/login", json={"matricula": "A000001", "senha": "errada"})
        print("login_invalido", r.status_code, r.json()["detail"])
        assert r.status_code == 401

        r = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        print("refresh", r.status_code)
        assert r.status_code == 200
        new_tokens = r.json()

        r = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        print("refresh_reuso", r.status_code)
        assert r.status_code == 401

        r = client.post("/api/auth/logout", json={"refresh_token": new_tokens["refresh_token"]})
        print("logout", r.status_code, r.json())
        assert r.status_code == 200
        print("OK")


if __name__ == "__main__":
    main()
