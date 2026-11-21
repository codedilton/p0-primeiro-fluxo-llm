"""Chamada ao provedor de IA e tratamento da resposta.

Prepara a solicitação, chama a API (endpoint compatível com OpenAI),
extrai o texto gerado e valida a categoria devolvida. Não conhece
terminais nem arquivos: quem orquestra é o main.

As falhas de comunicação e do serviço são convertidas nas exceções
de erros.py; nada de traceback técnico chega ao usuário.
"""

import requests

import prompts
from erros import (
    ErroAutenticacao,
    ErroComunicacao,
    ErroRespostaInvalida,
    ErroServicoIndisponivel,
)

# Códigos HTTP do provedor mapeados para os nossos tipos de erro.
# 4xx = o problema é do pedido (aqui, a credencial);
# 5xx = o problema é do serviço.
AUTENTICACAO_HTTP = {401, 403}
INDISPONIVEL_HTTP = {429, 500, 502, 503, 504}


def montar_solicitacao(mensagem: str, config: dict) -> dict:
    """Monta o corpo JSON da requisição de classificação."""
    return {
        "model": config["model"],
        "temperature": config["temperature"],
        "max_tokens": config["max_tokens"],
        "messages": [
            {"role": "system", "content": prompts.montar_prompt_sistema()},
            {"role": "user", "content": prompts.montar_prompt_usuario(mensagem)},
        ],
    }


def chamar_modelo(mensagem: str, config: dict) -> str:
    """Envia a mensagem ao provedor de IA e devolve o texto bruto gerado.

    Levanta ErroAutenticacao, ErroServicoIndisponivel, ErroComunicacao
    ou ErroRespostaInvalida conforme a falha observada.
    """
    corpo = montar_solicitacao(mensagem, config)

    headers = {}
    if not config.get("sem_autenticacao"):
        # A credencial vai só no header da requisição; nunca em log.
        headers["Authorization"] = f"Bearer {config['api_key']}"

    try:
        resposta = requests.post(
            config["api_url"],
            headers=headers,
            json=corpo,
            timeout=config["timeout"],
            verify=config.get("verificar_tls", True),
        )
    except requests.exceptions.SSLError as erro_ssl:
        # Certificado do ambiente interno sem confiança pública
        # (comum em redes privadas, com certificado próprio).
        if "certificate verify failed" in str(erro_ssl).lower():
            raise ErroComunicacao(
                "Certificado TLS do provedor de IA não pôde ser verificado. "
                "Se o ambiente interno usa certificado próprio, defina IA_TLS_VERIFY=0."
            ) from None
        raise ErroComunicacao(
            "Falha de SSL/TLS ao contatar o provedor de IA."
        ) from None
    except requests.exceptions.Timeout:
        raise ErroComunicacao(
            f"Tempo esgotado ({config['timeout']}s) ao contatar o provedor de IA."
        ) from None
    except requests.exceptions.ConnectionError:
        raise ErroComunicacao(
            "Não foi possível conectar ao provedor de IA. Verifique sua conexão."
        ) from None

    if resposta.status_code != 200:
        _levantar_erro_http(resposta)

    return extrair_texto(resposta.json())


def _levantar_erro_http(resposta) -> None:
    """Converte o código HTTP em uma exceção específica do programa."""
    status = resposta.status_code
    if status in AUTENTICACAO_HTTP:
        raise ErroAutenticacao(
            "Credencial inválida: o provedor de IA recusou a chave. "
            "Verifique o valor de IA_API_KEY no .env."
        )
    if status in INDISPONIVEL_HTTP:
        if status == 429:
            raise ErroServicoIndisponivel(
                "Limite de uso do provedor atingido. Aguarde alguns minutos e tente novamente."
            )
        raise ErroServicoIndisponivel(
            "O provedor de IA está indisponível no momento. Tente novamente mais tarde."
        )
    # Outros erros: mensagem genérica, mas sem expor segredos e sem traceback.
    raise ErroComunicacao(
        f"O provedor de IA respondeu com o código HTTP {status}. Tente novamente."
    )


def extrair_texto(dados: dict) -> str:
    """Extrai o texto gerado do JSON de resposta.

    O texto fica em choices[0].message.content. Modelos de raciocínio
    podem devolver content vazio quando o limite de tokens se esgota
    durante o raciocínio — nesse caso, é resposta inválida.
    """
    try:
        escolha = dados["choices"][0]
        texto = escolha["message"].get("content") or ""
    except (KeyError, IndexError, TypeError, AttributeError):
        raise ErroRespostaInvalida(
            "A resposta do provedor de IA veio em um formato inesperado."
        ) from None

    if not texto.strip():
        # Modelos de raciocínio podem esgotar o limite de tokens
        # "pensando" e devolver content vazio. O finish_reason conta
        # o que aconteceu: use-o para dar um diagnóstico acionável.
        motivo = escolha.get("finish_reason") or "desconhecido"
        if motivo == "length":
            raise ErroRespostaInvalida(
                "O modelo não devolveu texto: o limite de tokens se esgotou "
                "durante o raciocínio. Defina IA_MAX_TOKENS com um valor maior "
                "(ex.: 2048) e tente novamente."
            )
        raise ErroRespostaInvalida(
            f"O modelo não devolveu texto (motivo informado: {motivo}). Tente novamente."
        )
    return texto


def validar_categoria(texto_bruto: str) -> str:
    """Normaliza a resposta do modelo e confere a categoria.

    Normalização: espaços das pontas e caixa padronizada, para que
    "  Reclamação " bata com "reclamacao". Fora da lista combinada é
    resposta inválida, não categoria inventada.
    """
    categoria = texto_bruto.strip().lower()
    if categoria not in prompts.CATEGORIAS_VALIDAS:
        raise ErroRespostaInvalida(
            f"O modelo respondeu fora do combinado: {texto_bruto!r}"
        )
    return categoria
