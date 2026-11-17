"""Carregamento da configuração.

Centraliza a leitura do ambiente: carrega o arquivo .env (se existir),
valida o que é obrigatório e expõe os valores com fallbacks seguros.

Nenhuma credencial é impressa ou registrada em log.
"""

import os

from dotenv import load_dotenv

from erros import ErroConfiguracao

# Nome da variável de ambiente que carrega a credencial.
VARIAVEL_CHAVE = "IA_API_KEY"

# Valores padrão do provedor de IA (endpoint compatível com OpenAI).
PADRAO_API_URL = "https://api.groq.com/openai/v1/chat/completions"
PADRAO_MODEL = "openai/gpt-oss-20b"

# Parâmetros do modelo (ajustáveis sem tocar no núcleo).
TEMPERATURA = 0.0
MAX_TOKENS = 300
TIMEOUT_SEGUNDOS = 30


def carregar() -> dict:
    """Lê o .env e devolve a configuração validada do programa.

    Levanta ErroConfiguracao se algo obrigatório estiver ausente.
    """
    load_dotenv()

    api_key = (os.environ.get(VARIAVEL_CHAVE) or "").strip()
    if not api_key:
        raise ErroConfiguracao(
            f"Credencial ausente: defina {VARIAVEL_CHAVE} no arquivo .env "
            "(copie o .env.example como ponto de partida)."
        )

    api_url = (os.environ.get("IA_API_URL") or "").strip() or PADRAO_API_URL
    model = (os.environ.get("IA_MODEL") or "").strip() or PADRAO_MODEL

    return {
        "api_key": api_key,
        "api_url": api_url,
        "model": model,
        "temperature": TEMPERATURA,
        "max_tokens": MAX_TOKENS,
        "timeout": TIMEOUT_SEGUNDOS,
    }
