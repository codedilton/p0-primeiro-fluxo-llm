# p0-primeiro-fluxo-llm

**Classificador de mensagens de atendimento** — projeto P0 do curso de agentes de IA.

> Este programa recebe **a mensagem de um cliente ou colega** e devolve **uma de três categorias (dúvida, reclamação ou elogio)** para **quem atende ou organiza demandas**, que precisa disso porque **precisa priorizar e encaminhar mensagens sem ler todas manualmente**.

## Entrada e saída

- **Entrada:** uma mensagem em texto livre, digitada ou colada no terminal.
- **Saída:** a categoria da mensagem, exibida no terminal.

Exemplo de uso:

```
$ python3 src/main.py
Configuração carregada (modelo: openai/gpt-oss-20b).
Cole ou digite a mensagem a classificar: Comprei um produto e ele chegou quebrado. Ja mandei tres e-mails e ninguem responde. Quero meu dinheiro de volta!
Categoria: RECLAMAÇÃO
```

Mensagens que não se encaixam em nenhuma das três categorias recebem o rótulo "NÃO SE ENCAIXA EM NENHUMA CATEGORIA".

## Requisitos

- Python 3.10 ou superior
- Uma chave de API de um provedor de IA. O padrão do projeto é o [Groq](https://console.groq.com) (chave gratuita, sem cartão de crédito); outros provedores com endpoint compatível com OpenAI funcionam ajustando a configuração (ver abaixo).

## Instalação

```bash
git clone https://github.com/codedilton/p0-primeiro-fluxo-llm.git
cd p0-primeiro-fluxo-llm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuração

1. Copie o modelo de configuração e preencha a sua credencial:

```bash
cp .env.example .env
```

2. Edite o `.env` e defina `IA_API_KEY` com a chave do seu provedor de IA (no Groq, gere a chave em [console.groq.com/keys](https://console.groq.com/keys)). O `.env` **não** vai para o Git — está protegido pelo `.gitignore`.

3. Opcional: para usar outro provedor com endpoint compatível com OpenAI, defina também no `.env`:

```
IA_API_URL=https://do-seu-provedor.com/v1/chat/completions
IA_MODEL=nome-do-modelo
```

Nenhuma credencial fica no código: o programa carrega o `.env` automaticamente (via `python-dotenv`).

## Como executar

```bash
python3 src/main.py
```

O programa pede a mensagem, envia ao provedor de IA e mostra a categoria. Se a mensagem vier vazia, ele alerta e dá uma segunda tentativa.

## Organização do código

Cada responsabilidade do ciclo vive em um módulo próprio:

| Responsabilidade | Onde vive |
|---|---|
| Captura da entrada | `src/main.py` (`ler_entrada`) |
| Carregamento da configuração | `src/config.py` |
| Preparação da solicitação | `src/llm_client.py` (`montar_solicitacao`) |
| Chamada ao modelo | `src/llm_client.py` (`chamar_modelo`) |
| Tratamento da resposta | `src/llm_client.py` (`extrair_texto`, `validar_categoria`) |
| Apresentação do resultado | `src/main.py` (`exibir_resultado`) |

Módulos de apoio: `src/prompts.py` (categorias válidas e montagem do prompt) e `src/erros.py` (os seis tipos de erro com nome próprio).

## Tratamento de erros

Cada situação previsível tem uma exceção específica, uma mensagem compreensível e uma sugestão de próximo passo. Nenhum traceback técnico chega ao usuário; detalhes ficam disponíveis executando com `IA_DEBUG=1`.

| Situação | Exceção | Mensagem ao usuário |
|---|---|---|
| Credencial ausente | `ErroConfiguracao` | "Credencial ausente: defina IA_API_KEY no arquivo .env" |
| Credencial inválida (HTTP 401/403) | `ErroAutenticacao` | "Credencial inválida: o provedor de IA recusou a chave" |
| Limite de uso (HTTP 429) | `ErroServicoIndisponivel` | "Limite de uso do provedor atingido; aguarde e tente novamente" |
| Serviço fora do ar (HTTP 5xx) | `ErroServicoIndisponivel` | "O provedor de IA está indisponível no momento" |
| Timeout | `ErroComunicacao` | "Tempo esgotado ao contatar o provedor de IA" |
| Falha de rede | `ErroComunicacao` | "Não foi possível conectar; verifique sua conexão" |
| Resposta vazia ou inesperada | `ErroRespostaInvalida` | "O modelo não devolveu texto" / "resposta em formato inesperado" |
| Entrada vazia (2 tentativas) | `ErroEntradaInvalida` | alerta na 1ª tentativa; encerramento controlado na 2ª |

## Testes

Os testes reais usam o serviço de verdade; os simulados verificam o comportamento sem rede (respostas e falhas fabricadas em memória). A distinção segue a especificação do nível Intermediário.

### Testes reais

| # | Situação | Esperado | Obtido |
|---|---|---|---|
| 1 | Reclamação real ("produto chegou quebrado... quero meu dinheiro de volta") | RECLAMAÇÃO | RECLAMAÇÃO ✓ |
| 2 | Dúvida real ("vocês têm na cor azul? qual o prazo?") | DÚVIDA | DÚVIDA ✓ |
| 3 | Credencial ausente (pasta sem `.env`) | Mensagem clara, sem chamada à API | "Credencial ausente: defina IA_API_KEY..." ✓ |
| 4 | Credencial inválida (chave falsa no `.env` → HTTP 401 real do serviço) | Mensagem clara, sem expor segredo | "Credencial inválida: o provedor de IA recusou a chave" ✓ |
| 5 | Entrada vazia duas vezes | Alerta na 1ª, encerramento controlado na 2ª | "Nenhuma mensagem foi fornecida após duas tentativas." ✓ |

### Testes simulados (sem rede)

| # | Situação simulada | Esperado | Obtido |
|---|---|---|---|
| 6 | Timeout do provedor | `ErroComunicacao` com mensagem amigável | ✓ |
| 7 | Falha de conexão | `ErroComunicacao` com mensagem amigável | ✓ |
| 8 | HTTP 503 (fora do ar) | `ErroServicoIndisponivel` | ✓ |
| 9 | HTTP 429 (limite) | `ErroServicoIndisponivel` | ✓ |
| 10 | JSON em formato inesperado | `ErroRespostaInvalida` | ✓ |
| 11 | Resposta vazia (content vazio) | `ErroRespostaInvalida` | ✓ |
| 12 | Categoria fora do combinado ("talvez") | `ErroRespostaInvalida` | ✓ |
| 13 | Normalização ("  Reclamacao  ") | categoria validada | ✓ |

## Roadmap

- [x] **Básico** — núcleo funcional: entrada → provedor de IA → saída, chave fora do código
- [x] **Intermediário** — módulos com responsabilidade única, seis tipos de erro tratados especificamente, `.env.example`, testes reais e simulados
- [ ] **Avançado** — testes automatizados na suíte, configuração externa dos parâmetros, registro de execução sem dados sensíveis, validação em ambiente limpo
