"""Erros específicos do classificador.

Cada tipo de falha previsível tem uma exceção com nome próprio. Os
módulos levantam o erro que descreve a situação; apenas o ponto de
entrada os captura e traduz para uma mensagem compreensível.

Hierarquia:

    ErroClassificador            (base comum)
    ├── ErroConfiguracao         (ambiente mal preparado)
    ├── ErroEntradaInvalida      (texto vazio)
    ├── ErroComunicacao          (rede, timeout)
    ├── ErroServicoIndisponivel  (provedor fora do ar, limite atingido)
    ├── ErroAutenticacao         (credencial ausente ou inválida)
    └── ErroRespostaInvalida     (resposta vazia ou fora do combinado)
"""


class ErroClassificador(Exception):
    """Base comum de todos os erros tratados pelo programa."""


class ErroConfiguracao(ErroClassificador):
    """Ambiente mal preparado: variável ausente, endpoint vazio etc."""


class ErroEntradaInvalida(ErroClassificador):
    """Entrada do usuário não atende ao que o programa precisa."""


class ErroComunicacao(ErroClassificador):
    """Falha de rede ou timeout ao contatar o provedor de IA."""


class ErroServicoIndisponivel(ErroClassificador):
    """Provedor de IA fora do ar ou limite de uso atingido."""


class ErroAutenticacao(ErroClassificador):
    """Credencial ausente ou recusada pelo provedor de IA."""


class ErroRespostaInvalida(ErroClassificador):
    """Resposta do modelo vazia, malformada ou fora do combinado."""
