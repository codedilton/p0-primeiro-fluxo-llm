"""Testes do prompt: blocos e categorias em um único lugar."""

import prompts


def test_prompt_anuncia_as_tres_categorias_e_o_caso_de_borda():
    p = prompts.montar_prompt_sistema().lower()
    assert "duvida" in p and "reclamacao" in p and "elogio" in p
    assert "invalida" in p


def test_prompt_usuario_envolve_a_mensagem():
    assert "Mensagem:" in prompts.montar_prompt_usuario("olá")


def test_categorias_validas_sincronizadas_com_o_prompt():
    """O que o prompt anuncia é exatamente o que a validação aceita."""
    p = prompts.montar_prompt_sistema().lower()
    for categoria in prompts.CATEGORIAS_VALIDAS:
        assert categoria in p
