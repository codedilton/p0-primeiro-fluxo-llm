"""Testes do cliente do provedor: mapeamento de erros e extração, sem rede."""

from unittest import mock

import pytest
import requests

import llm_client
from erros import (
    ErroAutenticacao,
    ErroComunicacao,
    ErroRespostaInvalida,
    ErroServicoIndisponivel,
)

CONFIG = {
    "api_key": "chave-de-teste",
    "api_url": "https://provedor.exemplo/v1/chat/completions",
    "model": "modelo-de-teste",
    "temperature": 0.0,
    "max_tokens": 300,
    "timeout": 30.0,
    "sem_autenticacao": False,
    "verificar_tls": True,
}


def resposta(status, corpo):
    fake = mock.Mock(spec=requests.Response)
    fake.status_code = status
    fake.json.return_value = corpo
    return fake


def test_montar_solicitacao_tem_formato_openai_e_nao_vaza_credencial():
    corpo = llm_client.montar_solicitacao("olá", CONFIG)
    assert corpo["model"] == "modelo-de-teste"
    assert corpo["temperature"] == 0.0
    assert corpo["max_tokens"] == 300
    assert corpo["messages"][0]["role"] == "system"
    assert corpo["messages"][1]["role"] == "user"
    assert "olá" in corpo["messages"][1]["content"]
    assert "api_key" not in str(corpo)


def test_extrair_texto_valido():
    corpo = {"choices": [{"message": {"role": "assistant", "content": "duvida"}}]}
    assert llm_client.extrair_texto(corpo) == "duvida"


def test_extrair_texto_de_json_estranho():
    with pytest.raises(ErroRespostaInvalida):
        llm_client.extrair_texto({"inesperado": True})


def test_extrair_texto_de_resposta_vazia():
    corpo = {"choices": [{"message": {"role": "assistant", "content": ""}}]}
    with pytest.raises(ErroRespostaInvalida):
        llm_client.extrair_texto(corpo)


def test_resposta_vazia_por_limite_de_tokens_dá_diagnóstico_acionável():
    corpo = {"choices": [{"message": {"role": "assistant", "content": ""},
                          "finish_reason": "length"}]}
    with pytest.raises(ErroRespostaInvalida, match="IA_MAX_TOKENS"):
        llm_client.extrair_texto(corpo)


def test_resposta_vazia_com_outro_motivo_informa_o_motivo():
    corpo = {"choices": [{"message": {"role": "assistant", "content": ""},
                          "finish_reason": "content_filter"}]}
    with pytest.raises(ErroRespostaInvalida, match="content_filter"):
        llm_client.extrair_texto(corpo)


@pytest.mark.parametrize("texto,esperado", [
    ("  Reclamacao  ", "reclamacao"),
    ("DUVIDA", "duvida"),
    ("Elogio", "elogio"),
])
def test_validar_categoria_normaliza(texto, esperado):
    assert llm_client.validar_categoria(texto) == esperado


def test_validar_categoria_rejeita_fora_do_combinado():
    with pytest.raises(ErroRespostaInvalida):
        llm_client.validar_categoria("talvez")


def test_401_vira_erro_autenticacao():
    with mock.patch.object(llm_client.requests, "post", return_value=resposta(401, {})):
        with pytest.raises(ErroAutenticacao):
            llm_client.chamar_modelo("oi", CONFIG)


def test_429_vira_erro_indisponivel():
    with mock.patch.object(llm_client.requests, "post", return_value=resposta(429, {})):
        with pytest.raises(ErroServicoIndisponivel):
            llm_client.chamar_modelo("oi", CONFIG)


def test_503_vira_erro_indisponivel():
    with mock.patch.object(llm_client.requests, "post", return_value=resposta(503, {})):
        with pytest.raises(ErroServicoIndisponivel):
            llm_client.chamar_modelo("oi", CONFIG)


def test_timeout_vira_erro_comunicacao():
    with mock.patch.object(llm_client.requests, "post", side_effect=requests.exceptions.Timeout()):
        with pytest.raises(ErroComunicacao):
            llm_client.chamar_modelo("oi", CONFIG)


def test_falha_de_rede_vira_erro_comunicacao():
    with mock.patch.object(llm_client.requests, "post", side_effect=requests.exceptions.ConnectionError()):
        with pytest.raises(ErroComunicacao):
            llm_client.chamar_modelo("oi", CONFIG)


def test_certificado_invalido_vira_erro_com_dica_da_flag():
    erro = requests.exceptions.SSLError("(SSL) certificate verify failed: certificado próprio")
    with mock.patch.object(llm_client.requests, "post", side_effect=erro):
        with pytest.raises(ErroComunicacao, match="IA_TLS_VERIFY"):
            llm_client.chamar_modelo("oi", CONFIG)


def test_sucesso_devolve_texto():
    corpo = {"choices": [{"message": {"role": "assistant", "content": "elogio"}}]}
    with mock.patch.object(llm_client.requests, "post", return_value=resposta(200, corpo)) as post:
        assert llm_client.chamar_modelo("oi", CONFIG) == "elogio"
    # Credencial vai no header, nunca no corpo; verify segue a configuração.
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer chave-de-teste"
    assert post.call_args.kwargs["verify"] is True


def test_sem_autenticacao_nao_envia_header():
    sem_auth = dict(CONFIG, sem_autenticacao=True, api_key="")
    corpo = {"choices": [{"message": {"role": "assistant", "content": "duvida"}}]}
    with mock.patch.object(llm_client.requests, "post", return_value=resposta(200, corpo)) as post:
        llm_client.chamar_modelo("oi", sem_auth)
    assert "Authorization" not in post.call_args.kwargs["headers"]
