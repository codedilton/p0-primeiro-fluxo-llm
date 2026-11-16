"""Classificador de mensagens de atendimento — P0, nível Básico.

Problema: recebe a mensagem de um cliente ou colega e devolve uma de
três categorias: duvida, reclamacao ou elogio.

Ciclo do programa (o "primeiro fluxo LLM"):
    entrada de texto -> chamada à API do LLM -> tratamento da resposta -> saída

Execução:
    export GROQ_API_KEY="sua-chave"   (ou use um arquivo .env)
    python3 src/main.py
"""

import os
import sys

import requests

# --- Configuração do serviço (fora do código fica só a chave) ---

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-20b"
TIMEOUT_SEGUNDOS = 30

# Categorias que o prompt aceita. "invalida" é a saída combinada para
# mensagens que não se encaixam em nenhuma das três.
CATEGORIAS_VALIDAS = {"duvida", "reclamacao", "elogio", "invalida"}

# Rótulos legíveis para exibir ao usuário.
ROTULOS = {
    "duvida": "DÚVIDA",
    "reclamacao": "RECLAMAÇÃO",
    "elogio": "ELOGIO",
    "invalida": "NÃO SE ENCAIXA EM NENHUMA CATEGORIA",
}

# O prompt segue 5 blocos: papel, tarefa, regras, caso de borda e entrada.
# O caso de borda (INVALIDA) é o que permite detectar mensagens fora do escopo.
PROMPT_SISTEMA = (
    "Você é um classificador de mensagens de atendimento. "
    "Classifique a mensagem abaixo em exatamente uma categoria. "
    "Categorias válidas: duvida, reclamacao, elogio, invalida. "
    "Se a mensagem não se encaixar em nenhuma, responda: INVALIDA. "
    "Responda apenas com a categoria, em minúsculas, sem pontuação "
    "e sem nenhuma outra palavra."
)

# Modelo de raciocínio: gasta tokens "pensando" antes de responder,
# por isso max_tokens precisa ser maior que o tamanho da resposta final.
MAX_TOKENS = 300
TEMPERATURA = 0.0  # classificação: mesma mensagem deve gerar a mesma categoria


def ler_entrada() -> str:
    """Lê a mensagem do usuário no terminal e remove espaços das pontas."""
    return input("Cole ou digite a mensagem a classificar: ").strip()


def chamar_llm(mensagem: str, api_key: str) -> str:
    """Envia a mensagem ao LLM e devolve o texto bruto da resposta."""
    resposta = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": MODEL,
            "temperature": TEMPERATURA,
            "max_tokens": MAX_TOKENS,
            "messages": [
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": mensagem},
            ],
        },
        timeout=TIMEOUT_SEGUNDOS,
    )

    if resposta.status_code != 200:
        # Tratamento completo de erros chega no nível Intermediário;
        # por ora, mostramos o status e o texto devolvido pelo serviço.
        sys.exit(f"Erro HTTP {resposta.status_code}: {resposta.text}")

    dados = resposta.json()
    # O texto gerado fica em choices[0].message.content. O modelo de
    # raciocínio pode devolver content vazio se gastar tokens pensando;
    # por isso o "or ''".
    return dados["choices"][0]["message"].get("content") or ""


def main() -> None:
    # Credencial fora do código: vem do ambiente (ou de um .env carregado
    # antes da execução). Sem ela, o programa nem tenta chamar a API.
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        sys.exit('Defina a variável GROQ_API_KEY no ambiente (ex.: export GROQ_API_KEY="sua-chave").')

    mensagem = ler_entrada()
    if not mensagem:
        sys.exit("Forneça um texto válido: a mensagem não pode ser vazia.")

    categoria_bruta = chamar_llm(mensagem, api_key)

    # Normalização: o modelo pode responder com espaços ou maiúsculas
    # a mais (" Reclamação "). Padronizamos antes de validar.
    categoria = categoria_bruta.strip().lower()
    if categoria not in CATEGORIAS_VALIDAS:
        sys.exit(f"Resposta inesperada do modelo: {categoria_bruta!r}")

    print(f"Categoria: {ROTULOS[categoria]}")


if __name__ == "__main__":
    main()
