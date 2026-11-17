"""Montagem dos prompts do classificador.

O prompt segue cinco blocos: papel, tarefa, regras, caso de borda e
entrada. O caso de borda (INVALIDA) permite detectar mensagens fora
do escopo das tres categorias.

As categorias válidas vivem aqui, em um único lugar: o prompt que as
anuncia e a validação que as confere precisam estar sempre de acordo.
"""

CATEGORIAS_VALIDAS = {"duvida", "reclamacao", "elogio", "invalida"}

CATEGORIA_NAO_ENCAIXADA = "invalida"

PROMPT_SISTEMA = (
    "Você é um classificador de mensagens de atendimento. "
    "Classifique a mensagem abaixo em exatamente uma categoria. "
    "Categorias válidas: duvida, reclamacao, elogio, invalida. "
    "Se a mensagem não se encaixar em nenhuma, responda: INVALIDA. "
    "Responda apenas com a categoria, em minúsculas, sem pontuação "
    "e sem nenhuma outra palavra."
)


def montar_prompt_sistema() -> str:
    """Devolve as instruções de papel e regras do classificador."""
    return PROMPT_SISTEMA


def montar_prompt_usuario(mensagem: str) -> str:
    """Envolve a mensagem do usuário no bloco de entrada do prompt."""
    return f"Mensagem: {mensagem}"
