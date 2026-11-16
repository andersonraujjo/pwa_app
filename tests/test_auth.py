"""Testes de autenticação: login, refresh e logout."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"


def test_login_valido(client: TestClient) -> None:
    r = client.post(
        "/api/auth/login",
        json={"matricula": "A000001", "senha": "demo1234"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["expires_in"] > 0


def test_login_invalido(client: TestClient) -> None:
    r = client.post(
        "/api/auth/login",
        json={"matricula": "A000001", "senha": "senha-errada"},
    )
    assert r.status_code == 401
    assert "inválid" in r.json()["detail"].lower()


def test_login_matricula_inexistente_mensagem_generica(client: TestClient) -> None:
    r = client.post(
        "/api/auth/login",
        json={"matricula": "Z999999", "senha": "demo1234"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Matrícula ou senha inválidas"


def test_refresh_rotacao(client: TestClient, tokens_a1: dict) -> None:
    antigo = tokens_a1["refresh_token"]
    r = client.post("/api/auth/refresh", json={"refresh_token": antigo})
    assert r.status_code == 200
    novo = r.json()
    assert novo["access_token"]
    assert novo["refresh_token"]
    assert novo["refresh_token"] != antigo

    # Refresh antigo não pode ser reutilizado
    r2 = client.post("/api/auth/refresh", json={"refresh_token": antigo})
    assert r2.status_code == 401


def test_logout_revoga_refresh(client: TestClient, tokens_a1: dict) -> None:
    refresh = tokens_a1["refresh_token"]
    r = client.post("/api/auth/logout", json={"refresh_token": refresh})
    assert r.status_code == 200

    r2 = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 401
