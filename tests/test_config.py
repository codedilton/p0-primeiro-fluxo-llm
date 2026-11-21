"""Testes de configuração: sem rede, sem LLM, só ambiente."""

import pytest

import config
from erros import ErroConfiguracao


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch):
    """Remove influência do .env e de variáveis herdadas; .env não participa dos testes."""
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    for variavel in ("IA_API_KEY", "IA_API_URL", "IA_MODEL", "IA_NO_AUTH", "IA_TLS_VERIFY", "IA_TIMEOUT"):
        monkeypatch.delenv(variavel, raising=False)


def test_padroes_apontam_para_o_llm_interno(monkeypatch):
    monkeypatch.setenv("IA_NO_AUTH", "1")
    c = config.carregar()
    assert c["api_url"] == "https://llm-internal.softex:9001/v1/chat/completions"
    assert c["model"] == "qwen3.5:9b-q4_K_M"


def test_credencial_ausente_levanta_erro_configuracao():
    with pytest.raises(ErroConfiguracao):
        config.carregar()


def test_credencial_presente_configura_autenticacao(monkeypatch):
    monkeypatch.setenv("IA_API_KEY", "chave-de-teste")
    c = config.carregar()
    assert c["api_key"] == "chave-de-teste"
    assert c["sem_autenticacao"] is False


def test_endpoint_sem_credencial_aceito_com_ia_no_auth(monkeypatch):
    monkeypatch.setenv("IA_NO_AUTH", "1")
    c = config.carregar()
    assert c["api_key"] == ""
    assert c["sem_autenticacao"] is True


def test_tls_verificado_desligado_por_padrao(monkeypatch):
    # Certificado próprio do ambiente interno: verify=False por padrão.
    monkeypatch.setenv("IA_API_KEY", "chave-de-teste")
    assert config.carregar()["verificar_tls"] is False


def test_tls_verificado_reatavel(monkeypatch):
    monkeypatch.setenv("IA_API_KEY", "chave-de-teste")
    monkeypatch.setenv("IA_TLS_VERIFY", "1")
    assert config.carregar()["verificar_tls"] is True


def test_timeout_invalido_cai_no_padrao(monkeypatch):
    monkeypatch.setenv("IA_API_KEY", "chave-de-teste")
    monkeypatch.setenv("IA_TIMEOUT", "abc")
    assert config.carregar()["timeout"] == 30.0


def test_max_tokens_padrao_2048(monkeypatch):
    monkeypatch.setenv("IA_API_KEY", "chave-de-teste")
    assert config.carregar()["max_tokens"] == 2048


def test_max_tokens_configuravel(monkeypatch):
    monkeypatch.setenv("IA_API_KEY", "chave-de-teste")
    monkeypatch.setenv("IA_MAX_TOKENS", "4096")
    assert config.carregar()["max_tokens"] == 4096


def test_max_tokens_invalido_cai_no_padrao(monkeypatch):
    monkeypatch.setenv("IA_API_KEY", "chave-de-teste")
    monkeypatch.setenv("IA_MAX_TOKENS", "muito")
    assert config.carregar()["max_tokens"] == 2048
