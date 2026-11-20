"""Testes da aplicação web: rotas, validações e caminhos de erro — sem rede."""

from unittest import mock

import pytest

import webapp
from erros import ErroAutenticacao


@pytest.fixture()
def cliente():
    return webapp.app.test_client()


@pytest.fixture()
def config_falsa(monkeypatch):
    monkeypatch.setattr(
        webapp.config, "carregar",
        lambda: {"api_key": "chave-de-teste", "api_url": "http://x", "model": "m",
                 "temperature": 0.0, "max_tokens": 300, "timeout": 30.0,
                 "sem_autenticacao": False, "verificar_tls": True},
    )


def test_formulario_abre(cliente):
    r = cliente.get("/")
    assert r.status_code == 200
    assert "Classificar".encode() in r.data


def test_entrada_vazia_rejeitada(cliente):
    r = cliente.post("/", data={"mensagem": "  "})
    assert r.status_code == 400
    assert "não pode ser vazia".encode() in r.data


def test_entrada_muito_longa_rejeitada(cliente):
    r = cliente.post("/", data={"mensagem": "x" * 4001})
    assert r.status_code == 400
    assert "muito longa".encode() in r.data


def test_classificacao_exibida_na_pagina(cliente, config_falsa, monkeypatch):
    monkeypatch.setattr(webapp.llm_client, "chamar_modelo", lambda *a, **k: "reclamacao")
    monkeypatch.setattr(webapp.llm_client, "validar_categoria", lambda t: t)
    r = cliente.post("/", data={"mensagem": "produto quebrado, quero reembolso"})
    assert r.status_code == 200
    assert "RECLAMAÇÃO".encode() in r.data


def test_erro_do_provedor_exibido_sem_crash(cliente, config_falsa, monkeypatch):
    monkeypatch.setattr(
        webapp.llm_client, "chamar_modelo",
        mock.Mock(side_effect=ErroAutenticacao("Credencial inválida")),
    )
    r = cliente.post("/", data={"mensagem": "qualquer coisa"})
    assert r.status_code == 502
    assert "Credencial inválida".encode() in r.data


def test_health(cliente):
    r = cliente.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}
