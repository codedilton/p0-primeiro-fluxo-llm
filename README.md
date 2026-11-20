# p0-primeiro-fluxo-llm

**Classificador de mensagens de atendimento** — projeto P0 do curso de agentes de IA (níveis Básico, Intermediário e Avançado concluídos; entrega final em container Docker).

> Este programa recebe **a mensagem de um cliente ou colega** e devolve **uma de três categorias (dúvida, reclamação ou elogio)** para **quem atende ou organiza demandas**, que precisa disso porque **precisa priorizar e encaminhar mensagens sem ler todas manualmente**.

## Como usar (visão rápida)

A aplicação é **web**: abre no navegador, tem uma caixa de texto e um botão **Classificar**, e responde com a categoria da mensagem. Ela roda em container Docker e conversa com um provedor de IA compatível com OpenAI.

```
Navegador ──POST /──▶ aplicação (Flask + gunicorn) ──▶ provedor de IA ──▶ categoria na página
```

Padrões de conexão (ajustáveis por variável de ambiente, sem tocar no código):

| Variável | Padrão | Para quê |
|---|---|---|
| `IA_API_URL` | `https://llm-internal.softex:9001/v1/chat/completions` | Endpoint do provedor de IA (formato OpenAI). O endereço interno só é acessível de dentro da rede do container |
| `IA_MODEL` | `qwen3.5:9b-q4_K_M` | Modelo que classifica |
| `IA_API_KEY` | *(vazio)* | Credencial, se o provedor exigir |
| `IA_NO_AUTH` | `0` | `1` = endpoint sem credencial |
| `IA_TLS_VERIFY` | `0` | `0` = não verifica o certificado (o ambiente interno usa certificado próprio, sem cadeia pública — conforme o manual). `1` = verifica (provedores com TLS público) |
| `IA_TIMEOUT` | `30` | Timeout da chamada, em segundos |

## Requisitos

- **Para executar a entrega (container):** Docker
- **Para desenvolver localmente:** Python 3.10+ e Docker (para os testes de container)

Versões utilizadas no desenvolvimento: Python 3.12 (base da imagem), Flask 3.1.3, Gunicorn 27.0.1, requests 2.34.2, python-dotenv 1.2.4.

## Desenvolvimento local

```bash
git clone https://github.com/codedilton/p0-primeiro-fluxo-llm.git
cd p0-primeiro-fluxo-llm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # preencha as variáveis do seu provedor
python3 src/webapp.py     # http://localhost:8000
```

Credencial nenhuma fica no código: o `.env` (protegido pelo `.gitignore`) alimenta as variáveis localmente; no container, elas chegam pelo dashboard da plataforma.

## Execução em container

```bash
docker build -t ediltonsilvajrgmailcom:latest .
docker run --rm -p 8000:8000 \
  -e IA_API_URL="https://llm-internal.softex:9001/v1/chat/completions" \
  -e IA_MODEL="qwen3.5:9b-q4_K_M" \
  -e IA_NO_AUTH=1 -e IA_TLS_VERIFY=0 \
  ediltonsilvajrgmailcom:latest
# abra http://localhost:8000
```

## Entrega na plataforma (ambiente interno)

1. Salve a imagem em TAR (nome sem caracteres especiais, derivado do e-mail):

```bash
docker save --output ediltonsilvajrgmailcom.tar ediltonsilvajrgmailcom:latest
```

2. No dashboard, faça **Upload** do `.tar` (imagem de ~130MB, limite de 1024MB).
3. Configure **portas**: `8000` (a aplicação escuta em `0.0.0.0:8000`) e **variáveis de ambiente** (uma por linha, ex.: `IA_MODEL=qwen3.5:9b-q4_K_M`).
4. **Inicie** o container: ele entra na rede `llm-network` e passa a alcançar o LLM interno pelo hostname. Acesse a aplicação pelo endereço do servidor + porta pública indicada no dashboard.

Nota: dentro do container não há terminal — por isso a aplicação é web. Informações que precisam sobreviver a reinícios devem ficar em `/persistent` (este projeto não persiste nada).

## Organização do código

| Responsabilidade | Onde vive |
|---|---|
| Rotas web, entrada e apresentação | `src/webapp.py` + `src/templates/index.html` |
| Carregamento da configuração | `src/config.py` |
| Preparação da solicitação | `src/llm_client.py` (`montar_solicitacao`) |
| Chamada ao modelo | `src/llm_client.py` (`chamar_modelo`) |
| Tratamento da resposta | `src/llm_client.py` (`extrair_texto`, `validar_categoria`) |
| Prompt e categorias válidas | `src/prompts.py` |
| Seis tipos de erro com nome próprio | `src/erros.py` |
| Versão terminal (nível Intermediário, mantida) | `src/main.py` |

## Tratamento de erros

Cada situação previsível tem uma exceção específica, uma mensagem compreensível e uma sugestão de próximo passo. Na web, o erro aparece na própria página; nenhum traceback técnico chega ao usuário (detalhes ficam disponíveis com `IA_DEBUG=1`).

| Situação | Exceção | Mensagem ao usuário |
|---|---|---|
| Credencial ausente | `ErroConfiguracao` | "Credencial ausente: defina IA_API_KEY no ambiente (ou... IA_NO_AUTH=1)" |
| Credencial inválida (HTTP 401/403) | `ErroAutenticacao` | "Credencial inválida: o provedor de IA recusou a chave" |
| Limite de uso (HTTP 429) | `ErroServicoIndisponivel` | "Limite de uso do provedor atingido; aguarde e tente novamente" |
| Serviço fora do ar (HTTP 5xx) | `ErroServicoIndisponivel` | "O provedor de IA está indisponível no momento" |
| Timeout | `ErroComunicacao` | "Tempo esgotado ao contatar o provedor de IA" |
| Falha de rede | `ErroComunicacao` | "Não foi possível conectar; verifique sua conexão" |
| Certificado TLS não verificado | `ErroComunicacao` | "...Se o ambiente interno usa certificado próprio, defina IA_TLS_VERIFY=0" |
| Resposta vazia ou inesperada | `ErroRespostaInvalida` | "O modelo não devolveu texto" / "resposta em formato inesperado" |
| Entrada vazia / muito longa | validação na rota | mensagem inline na página (HTTP 400) |

## Testes

A suíte automatizada exercita a **lógica local sem nenhuma chamada real ao LLM** (respostas e falhas fabricadas em memória), conforme o enunciado do Avançado:

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
# 32 passed
```

Cobertura: prompt (blocos e sincronia com as categorias), configuração (padrões do ambiente interno, credencial ausente/presente, flags TLS/auth, timeout inválido), cliente (formato OpenAI, mapeamento de 401/429/503/timeout/rede/SSL, extração e normalização da resposta, credencial só no header) e rotas web (formulário, entradas inválidas, erro do provedor exibido sem crash, `/health`).

Testes **reais** registrados no [RELATORIO_EXECUCAO.md](RELATORIO_EXECUCAO.md): classificação de verdade (Groq como provedor público de teste), HTTP 401 autêntico com chave inválida e a mesma bateria **dentro do container** (formulário, classificação via HTTP, `/health`, erro amigável sem credencial, logs limpos). O teste final contra o LLM interno ocorre naturalmente após o upload, de dentro da rede do ambiente.

## Roadmap

- [x] **Básico** — núcleo funcional no terminal, chave fora do código, tag `p0-basico`
- [x] **Intermediário** — módulos com responsabilidade única, seis tipos de erro, testes reais e simulados, tag `p0-intermediario`
- [x] **Avançado + 3ª etapa** — aplicação web em container Docker, configuração 100% por variáveis de ambiente, suíte automatizada sem rede, validação em ambiente limpo (container), tag `p0-avancado`
