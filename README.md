# p0-primeiro-fluxo-llm

**Classificador de mensagens de atendimento** — projeto P0 do curso de agentes de IA.

> Este programa recebe **a mensagem de um cliente ou colega** e devolve **uma de três categorias (dúvida, reclamação ou elogio)** para **quem atende ou organiza demandas**, que precisa disso porque **precisa priorizar e encaminhar mensagens sem ler todas manualmente**.

## Entrada e saída

- **Entrada:** uma mensagem em texto livre, digitada ou colada no terminal.
- **Saída:** a categoria da mensagem, exibida no terminal.

Exemplo de uso:

```
$ python3 src/main.py
Cole ou digite a mensagem a classificar: Comprei um produto e ele chegou quebrado. Ja mandei tres e-mails e ninguem responde. Quero meu dinheiro de volta!
Categoria: RECLAMAÇÃO
```

Mensagens que não se encaixam em nenhuma das três categorias recebem o rótulo "NÃO SE ENCAIXA EM NENHUMA CATEGORIA".

## Requisitos

- Python 3.10 ou superior
- Uma chave de API do [Groq](https://console.groq.com) (gratuita, sem cartão de crédito)

## Instalação

```bash
git clone https://github.com/codedilton/p0-primeiro-fluxo-llm.git
cd p0-primeiro-fluxo-llm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuração

1. Crie uma conta em [console.groq.com](https://console.groq.com) e gere uma chave em [console.groq.com/keys](https://console.groq.com/keys).
2. Exporte a chave como variável de ambiente (ela **não** fica no código):

```bash
export GROQ_API_KEY="sua-chave-aqui"
```

Alternativa: coloque a linha `GROQ_API_KEY=sua-chave-aqui` em um arquivo `.env` na raiz do projeto e carregue-o antes de executar:

```bash
set -a; source .env; set +a
```

## Como executar

```bash
python3 src/main.py
```

O programa pede a mensagem, envia ao LLM e mostra a categoria.

## Como funciona

O fluxo em `src/main.py`:

```
entrada de texto  →  chamada à API do LLM  →  tratamento da resposta  →  saída
```

- **Serviço:** API do Groq, endpoint compatível com OpenAI (`/openai/v1/chat/completions`).
- **Modelo:** `openai/gpt-oss-20b` — pequeno e rápido, adequado a classificação.
- **Parâmetros:** `temperature 0.0` (classificação deve ser consistente: a mesma mensagem gera sempre a mesma categoria) e `max_tokens 300` (o modelo raciocina antes de responder, e o raciocínio consome tokens além da resposta final, que é uma única palavra).
- **Prompt:** papel + tarefa + regras + caso de borda (mensagens fora do escopo → `INVALIDA`) + mensagem do usuário.
- **Validação:** a resposta do modelo é normalizada (`strip().lower()`) e conferida contra a lista de categorias válidas antes de ser exibida.

## Testes manuais realizados

Cada caso: entrada → comportamento esperado → comportamento obtido.

| # | Entrada | Esperado | Obtido |
|---|---|---|---|
| 1 | Reclamação de produto quebrado sem resposta do suporte | RECLAMAÇÃO | RECLAMAÇÃO ✓ |
| 2 | Elogio ao atendimento | ELOGIO | ELOGIO ✓ |
| 3 | Pergunta sobre cor disponível e prazo de entrega | DÚVIDA | DÚVIDA ✓ |
| 4 | Entrada vazia (Enter sem digitar) | Mensagem clara, sem chamada à API | "Forneça um texto válido" ✓ |
| 5 | Execução sem `GROQ_API_KEY` definida | Mensagem clara, sem chamada à API | "Defina a variável GROQ_API_KEY..." ✓ |

## Roadmap

- [x] **Básico** — núcleo funcional: entrada → LLM → saída, chave fora do código
- [ ] **Intermediário** — funções com responsabilidade única, tratamento específico de erros (autenticação, rede, indisponibilidade, resposta inesperada)
- [ ] **Avançado** — testes automatizados, `.env.example`, README completo, branch + pull request, documento de decisões
