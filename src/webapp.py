"""Aplicação web do classificador — P0, 3ª etapa (container Docker).

O programa passa a escutar HTTP em 0.0.0.0 (exigência do ambiente
de containers: dentro dele ninguém digita no terminal). O núcleo de
classificação continua nos módulos config/llm_client/prompts/erros.

Rotas:
    GET  /       -> formulário de classificação (HTML sem JavaScript)
    POST /       -> classifica a mensagem e renderiza o resultado
    GET  /health -> verificação de vida (usada pelo HEALTHCHECK)

Execução local:
    python3 src/webapp.py                 (servidor de desenvolvimento)
Execução em container:
    gunicorn -w 2 -b 0.0.0.0:8000 webapp:app
"""

from flask import Flask, redirect, render_template, request, url_for

import config
import llm_client
from erros import ErroClassificador

app = Flask(__name__)

ROTULOS = {
    "duvida": "DÚVIDA",
    "reclamacao": "RECLAMAÇÃO",
    "elogio": "ELOGIO",
    "invalida": "NÃO SE ENCAIXA EM NENHUMA CATEGORIA",
}

#Limite de tamanho da mensagem (evita payloads absurdos).
MAX_CARACTERES = 4000


def classificar_mensagem(mensagem: str, configuracao: dict) -> str:
    """Percorre o ciclo completo e devolve o rótulo legível da categoria."""
    texto_bruto = llm_client.chamar_modelo(mensagem, configuracao)
    categoria = llm_client.validar_categoria(texto_bruto)
    return ROTULOS[categoria]


@app.route("/")
def formulario():
    """Página principal: formulário vazio ou com resultado da classificação."""
    return render_template("index.html", resultado=None, mensagem_enviada=None, erro=None)


@app.route("/", methods=["POST"])
def classificar_rota():
    """Recebe a mensagem do formulário e exibe o resultado ou o erro."""
    mensagem = (request.form.get("mensagem") or "").strip()

    if not mensagem:
        return render_template(
            "index.html",
            resultado=None,
            mensagem_enviada=None,
            erro="Forneça um texto válido: a mensagem não pode ser vazia.",
        ), 400
    if len(mensagem) > MAX_CARACTERES:
        return render_template(
            "index.html",
            resultado=None,
            mensagem_enviada=None,
            erro=f"Mensagem muito longa ({len(mensagem)} caracteres; máximo {MAX_CARACTERES}).",
        ), 400

    try:
        configuracao = config.carregar()
        resultado = classificar_mensagem(mensagem, configuracao)
    except ErroClassificador as erro:
        # Cada erro já sai dos módulos com mensagem compreensível;
        # aqui apenas o exibimos na própria página.
        return render_template(
            "index.html",
            resultado=None,
            mensagem_enviada=mensagem,
            erro=str(erro),
        ), 502

    return render_template("index.html", resultado=resultado, mensagem_enviada=mensagem, erro=None)


@app.route("/health")
def health():
    """Verificação de vida para o HEALTHCHECK do container."""
    return {"status": "ok"}, 200


if __name__ == "__main__":
    # Servidor de desenvolvimento, apenas para rodar fora de container.
    app.run(host="0.0.0.0", port=8000)
