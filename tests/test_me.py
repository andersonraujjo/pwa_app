"""Testes das rotas /api/me — proteção e isolamento entre alunos."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_me_protegida_sem_token(client: TestClient) -> None:
    r = client.get("/api/me")
    assert r.status_code == 401


def test_me_com_token(client: TestClient, auth_a1: dict[str, str]) -> None:
    r = client.get("/api/me", headers=auth_a1)
    assert r.status_code == 200
    body = r.json()
    assert body["matricula"] == "A000001"
    assert body["nome"] == "Aluno Exemplo"
    assert body["curso"]["codigo"] == "ADS000"


def test_isolamento_chamado_entre_alunos(
    client: TestClient,
    auth_a1: dict[str, str],
    auth_a2: dict[str, str],
) -> None:
    # A000001 cria um chamado
    r = client.post(
        "/api/me/chamados",
        headers=auth_a1,
        json={
            "setor": "Secretaria",
            "tipo": "Outros",
            "urgencia": "baixa",
            "descricao": "Chamado de isolamento entre alunos no pytest",
        },
    )
    assert r.status_code == 201
    chamado_id = r.json()["id"]
    protocolo = r.json()["protocolo"]
    assert protocolo.startswith("CH-")

    # Dono acessa
    r_ok = client.get(f"/api/me/chamados/{chamado_id}", headers=auth_a1)
    assert r_ok.status_code == 200
    assert r_ok.json()["protocolo"] == protocolo

    # Outro aluno não vê
    r_out = client.get(f"/api/me/chamados/{chamado_id}", headers=auth_a2)
    assert r_out.status_code == 404


def test_criar_e_listar_chamado(client: TestClient, auth_a1: dict[str, str]) -> None:
    r = client.post(
        "/api/me/chamados",
        headers=auth_a1,
        json={
            "setor": "Financeiro",
            "tipo": "Financeiro",
            "urgencia": "media",
            "descricao": "Teste de criação de chamado via API",
        },
    )
    assert r.status_code == 201
    criado = r.json()
    assert criado["status"] == "aberto"
    assert len(criado["eventos"]) >= 1

    r_lista = client.get("/api/me/chamados", headers=auth_a1)
    assert r_lista.status_code == 200
    ids = [c["id"] for c in r_lista.json()]
    assert criado["id"] in ids


def test_me_dados_nao_vazam_entre_alunos(
    client: TestClient,
    auth_a1: dict[str, str],
    auth_a2: dict[str, str],
) -> None:
    me1 = client.get("/api/me", headers=auth_a1).json()
    me2 = client.get("/api/me", headers=auth_a2).json()
    assert me1["matricula"] == "A000001"
    assert me2["matricula"] == "A000002"
    assert me1["email"] != me2["email"]


def test_carteira_e_notas(client: TestClient, auth_a1: dict[str, str]) -> None:
    r = client.get("/api/me/carteira", headers=auth_a1)
    assert r.status_code == 200
    carteira = r.json()
    assert "<svg" in carteira["qr_svg"].lower()
    assert carteira["matricula"] == "A000001"

    r2 = client.get("/api/me/notas", headers=auth_a1)
    assert r2.status_code == 200
    notas = r2.json()
    assert len(notas) >= 1
    assert "frequencia" in notas[0]
