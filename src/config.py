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
# Padrão da 3ª etapa: LLM interno do ambiente Softex (llm-network).
PADRAO_API_URL = "https://llm-internal.softex:9001/v1/chat/completions"
PADRAO_MODEL = "qwen3.5:9b-q4_K_M"

# Parâmetros do modelo (ajustáveis sem tocar no núcleo).
TEMPERATURA = 0.0
MAX_TOKENS = 300
TIMEOUT_SEGUNDOS = 30


def _flag(nome: str, padrao: str) -> bool:
    """Lê uma flag booleana do ambiente ("1"/"true" ligam; resto desliga)."""
    return (os.environ.get(nome) or padrao).strip().lower() in ("1", "true", "yes", "sim")


def carregar() -> dict:
    """Lê o ambiente (variáveis e .env, se existir) e devolve a configuração validada.

    No container, os valores chegam como variáveis de ambiente do
    dashboard (IA_API_URL, IA_MODEL, IA_API_KEY, IA_NO_AUTH,
    IA_TLS_VERIFY, IA_TIMEOUT); localmente, continuam podendo vir do
    arquivo .env. Levanta ErroConfiguracao se algo obrigatório faltar.
    """
    load_dotenv()

    api_url = (os.environ.get("IA_API_URL") or "").strip() or PADRAO_API_URL
    model = (os.environ.get("IA_MODEL") or "").strip() or PADRAO_MODEL
    api_key = (os.environ.get("IA_API_KEY") or "").strip()
    sem_autenticacao = _flag("IA_NO_AUTH", "0")
    # Padrão "0" (verify=False): o endpoint interno do ambiente usa
    # certificado próprio, sem cadeia pública. IA_TLS_VERIFY=1 reativa
    # a verificação para provedores com TLS público (ex.: Groq).
    verificar_tls = _flag("IA_TLS_VERIFY", "0")

    if not sem_autenticacao and not api_key:
        raise ErroConfiguracao(
            f"Credencial ausente: defina {VARIAVEL_CHAVE} no ambiente "
            "(ou, se o endpoint interno não exige credencial, defina IA_NO_AUTH=1)."
        )

    timeout_bruto = (os.environ.get("IA_TIMEOUT") or "").strip()
    timeout = float(timeout_bruto) if timeout_bruto.replace(".", "", 1).isdigit() else TIMEOUT_SEGUNDOS

    return {
        "api_key": api_key,
        "api_url": api_url,
        "model": model,
        "temperature": TEMPERATURA,
        "max_tokens": MAX_TOKENS,
        "timeout": timeout,
        "sem_autenticacao": sem_autenticacao,
        "verificar_tls": verificar_tls,
    }
