"""Classificador de mensagens de atendimento — P0, nível Intermediário.

Problema: recebe a mensagem de um cliente ou colega e devolve uma de
três categorias: duvida, reclamacao ou elogio.

Responsabilidades separadas por módulo (enunciado do Intermediário):

    captura da entrada ............ main  (ler_entrada, exibir_*)
    carregamento da config ........ config
    preparação da solicitação ..... llm_client.montar_solicitacao
    chamada ao modelo ............. llm_client.chamar_modelo
    tratamento da resposta ........ llm_client.extrair_texto/validar_categoria
    apresentação do resultado ..... main

Execução:
    cp .env.example .env   (e preencha IA_API_KEY)
    python3 src/main.py
"""

import os
import sys

import config
import llm_client
from erros import (
    ErroAutenticacao,
    ErroClassificador,
    ErroComunicacao,
    ErroConfiguracao,
    ErroEntradaInvalida,
    ErroRespostaInvalida,
    ErroServicoIndisponivel,
)

# Rótulos legíveis para exibir ao usuário.
ROTULOS = {
    "duvida": "DÚVIDA",
    "reclamacao": "RECLAMAÇÃO",
    "elogio": "ELOGIO",
    "invalida": "NÃO SE ENCAIXA EM NENHUMA CATEGORIA",
}

MAX_TENTATIVAS_ENTRADA = 2


def ler_entrada(tentativa: int) -> str:
    """Lê a mensagem no terminal e devolve o texto sem espaços das pontas.

    O alerta de mensagem vazia e a segunda tentativa ficam no main;
    aqui é apenas captura de entrada.
    """
    if tentativa > 1:
        return input("Última tentativa — digite a mensagem a classificar: ").strip()
    return input("Cole ou digite a mensagem a classificar: ").strip()


def carregar_configuracao() -> dict:
    """Delega ao módulo config e confirma o carregamento ao usuário."""
    configuracao = config.carregar()
    print(f"Configuração carregada (modelo: {configuracao['model']}).")
    return configuracao


def classificar(mensagem: str, configuracao: dict) -> str:
    """Percorre o ciclo completo e devolve a categoria validada."""
    texto_bruto = llm_client.chamar_modelo(mensagem, configuracao)
    return llm_client.validar_categoria(texto_bruto)


def exibir_resultado(categoria: str) -> None:
    """Apresenta a categoria ao usuário com rótulo legível."""
    print(f"Categoria: {ROTULOS[categoria]}")


def dica_do_erro(erro: Exception) -> str:
    """Sugestão de próximo passo para cada tipo de falha."""
    if isinstance(erro, ErroConfiguracao):
        return "Copie o .env.example para .env e preencha a credencial."
    if isinstance(erro, ErroAutenticacao):
        return "Gere uma nova chave no seu provedor e atualize o .env."
    if isinstance(erro, ErroComunicacao):
        return "Verifique sua conexão e execute o programa novamente."
    if isinstance(erro, ErroServicoIndisponivel):
        return "Aguarde alguns minutos antes de tentar novamente."
    if isinstance(erro, ErroRespostaInvalida):
        return "Se persistir, tente novamente — pode ser instabilidade temporária do provedor."
    if isinstance(erro, ErroEntradaInvalida):
        return "Execute o programa novamente e digite uma mensagem."
    return ""


def encerrar_com_erro(erro: ErroClassificador) -> None:
    """Traduz o erro para mensagem amigável e encerra de forma controlada.

    Nenhum traceback técnico chega ao usuário; os detalhes ficam
    disponíveis em modo de depuração (variável IA_DEBUG=1).
    """
    print(f"\nErro: {erro}")
    dica = dica_do_erro(erro)
    if dica:
        print(f"Sugestão: {dica}")
    if os.environ.get("IA_DEBUG") == "1":
        import traceback

        traceback.print_exc()
    sys.exit(1)


def main() -> None:
    try:
        configuracao = carregar_configuracao()

        mensagem = ""
        for tentativa in range(1, MAX_TENTATIVAS_ENTRADA + 1):
            mensagem = ler_entrada(tentativa)
            if mensagem:
                break
            if tentativa < MAX_TENTATIVAS_ENTRADA:
                print("A mensagem está vazia. Você tem mais uma tentativa.\n")

        if not mensagem:
            raise ErroEntradaInvalida(
                "Nenhuma mensagem foi fornecida após duas tentativas."
            )

        categoria = classificar(mensagem, configuracao)
        exibir_resultado(categoria)

    except ErroClassificador as erro:
        encerrar_com_erro(erro)
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")
        sys.exit(130)


if __name__ == "__main__":
    main()
