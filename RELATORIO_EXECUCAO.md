# Relatório de Execução — P0 Primeiro Fluxo LLM

**Projeto:** Classificador de mensagens de atendimento (dúvida, reclamação ou elogio)
**Repositório:** https://github.com/codedilton/p0-primeiro-fluxo-llm
**Estado:** nível Avançado concluído e lançado (tag `p0-avancado`), incluindo a 3ª etapa do curso (aplicação web em container Docker para o ambiente interno Softex). Histórico: Básico (`p0-basico`) e Intermediário (`p0-intermediario`).

## Evolução por nível

### Básico — concluído

- Núcleo funcional completo: lê a mensagem no terminal, envia à API do LLM (Groq, endpoint compatível com OpenAI) e exibe a categoria validada.
- Chave de API fora do código: lida da variável de ambiente `GROQ_API_KEY`, com `.gitignore` protegendo o `.env` desde o primeiro commit.
- Dependências declaradas (`requirements.txt`) e README que permite a outra pessoa instalar, configurar e executar sem ajuda.
- Fluxo de Git praticado desde o primeiro marco: branch `feature/nucleo-basico`, pull request #1 e tag `p0-basico`.

### Intermediário — concluído

- Código reorganizado em módulos com responsabilidade única: `main.py` (entrada e apresentação), `config.py` (carregamento e validação da configuração), `llm_client.py` (preparação da solicitação, chamada ao modelo e tratamento da resposta), `prompts.py` (prompt e categorias válidas) e `erros.py` (hierarquia de exceções).
- Seis tipos de erro com tratamento específico e mensagem compreensível: configuração, credencial inválida, indisponibilidade do serviço, limite de uso, falha de comunicação/timeout e resposta vazia ou inesperada — além da entrada vazia, com alerta na primeira tentativa e encerramento controlado na segunda.
- Nenhum traceback técnico chega ao usuário; cada erro vem com sugestão de próximo passo e os detalhes técnicos ficam atrás da variável `IA_DEBUG=1`.
- `.env.example` sem credenciais reais; `.env` carregado automaticamente via `python-dotenv`; nenhum segredo exposto em mensagens.
- Cenários de credencial ausente e inválida demonstrados com **testes reais**; indisponibilidade, timeout e respostas inválidas demonstrados com **testes simulados** sem rede, conforme a especificação.
- Branch `feature/tratamento-erros` integrada à principal por pull request (segundo PR do projeto).

### Avançado (com 3ª etapa: web + Docker) — concluído

- **Aplicação web:** o classificador passou a escutar HTTP em `0.0.0.0:8000` (exigência do ambiente de containers, onde não há terminal). Interface única em Flask: formulário POST sem JavaScript, resultado ou erro na mesma página, rota `/health` para verificação de vida. A lógica de negócio dos módulos permaneceu intacta — apenas a "casca" de interação trocou.
- **LLM interno:** padrões de configuração apontados para o endpoint interno do ambiente (`https://llm-internal.softex:9001/v1/chat/completions`, modelo `qwen3.5:9b-q4_K_M`), acessível somente de dentro da rede do container.
- **TLS do ambiente interno:** o certificado próprio do ambiente não tem cadeia pública; por padrão a verificação fica desligada (`IA_TLS_VERIFY=0`, conforme o manual) e o erro de verificação de certificado virou mensagem clara sugerindo a flag — não crash técnico.
- **Container:** `Dockerfile` com base `python:3.12-slim`, gunicorn (WSGI de produção) em `0.0.0.0:8000`, usuário não-root, `HEALTHCHECK`, `.dockerignore` que garante que `.env`, materiais do curso e histórico do Git nunca viram camada de imagem. Imagem final: **130MB** (limite da plataforma: 1024MB).
- **Testes automatizados:** suíte com **32 testes** (`pytest`) que exercem prompt, configuração, cliente do provedor (erros HTTP/rede/TLS simulados) e rotas web — **sem nenhuma chamada real ao LLM**, como o enunciado pede.
- **Validação em ambiente limpo:** a imagem foi construída do zero e a aplicação testada **dentro do container** (formulário, classificação real, `/health`, erro amigável sem credencial, logs sem segredos) — simulação fiel do fluxo de upload e execução da plataforma.
- **Configurações sem tocar no núcleo:** endpoint, modelo, credencial, timeout e flags de TLS/auth são todas variáveis de ambiente (`.env` local ou dashboard da plataforma), atendendo ao requisito do Avançado.
- Branch `feature/web-docker` integrada à principal por pull request (terceiro PR do projeto); entrega empacotada com `docker save` (`ediltonsilvajrgmailcom.tar`, 129MB).

## Decisões principais

**1. Recorte do problema**
- Decisão: classificar uma mensagem em exatamente três categorias, com saída `INVALIDA` para o que não se encaixa.
- Alternativa considerada: problemas mais amplos (assistente de estudos, gerenciador de tarefas com IA).
- Justificativa: cabe em uma frase, tem saída avaliável e exige interpretação de linguagem livre — caso em que o LLM agrega de fato, e regex não resolve.

**2. Acesso ao LLM: HTTP direto em vez de SDK**
- Decisão: chamada REST com a biblioteca `requests` ao endpoint compatível com OpenAI do Groq.
- Alternativa considerada: SDK oficial do provedor.
- Justificativa: a competência C03 é sobre APIs REST; enxergar endpoint, headers e corpo JSON ensina a mecânica e o conhecimento é portável entre provedores.

**3. Modelo e parâmetros**
- Decisão: `openai/gpt-oss-20b`, `temperature 0.0` e `max_tokens 300`.
- Alternativa considerada: `llama-3.1-8b-instant` com `max_tokens 10` (sugestão inicial da aula).
- Justificativa: o modelo sugerido não existe mais na conta (404); o `gpt-oss-20b` é um modelo de raciocínio e o raciocínio consome tokens, então o limite precisa acomodá-lo. `temperature 0.0` porque classificação exige consistência: mesma mensagem, mesma categoria.

**4. Validação da resposta no programa**
- Decisão: normalizar a resposta (`strip`/`lower`) e validar contra a lista de categorias antes de exibir; resposta fora da lista vira erro.
- Alternativa considerada: confiar no texto do modelo e exibi-lo diretamente.
- Justificativa: o modelo é um gerador de texto e pode responder fora do formato combinado; a validação transforma isso em erro controlado, não em saída errada para o usuário.

**5. Fluxo de versionamento**
- Decisão: um branch por marco e pull request mesmo trabalhando sozinho.
- Alternativa considerada: commits diretos na `master`.
- Justificativa: o histórico deve contar a evolução do projeto (C02), e o PR documenta o que mudou em cada etapa — além de treinar o fluxo usado em times reais.

**6. Hierarquia de exceções próprias (Intermediário)**
- Decisão: criar seis exceções com nome próprio (`ErroConfiguracao`, `ErroAutenticacao`, `ErroComunicacao`, `ErroServicoIndisponivel`, `ErroRespostaInvalida`, `ErroEntradaInvalida`), levantadas nos módulos e traduzidas em mensagens amigáveis apenas no ponto de entrada.
- Alternativa considerada: manter `sys.exit` com texto fixo em cada ponto de falha (estilo do Básico) ou um único `except Exception` genérico.
- Justificativa: separa *detectar* a falha (módulo técnico) de *explicá-la* (interface); cada tipo nasce em um único lugar, com mensagem e sugestão próprias; e abre caminho para os testes automatizados do Avançado.

**7. Nomes genéricos de provedor na interface (Intermediário)**
- Decisão: mensagens, variáveis (`IA_API_KEY`, `IA_API_URL`, `IA_MODEL`) e documentação falam de "provedor de IA"; o endpoint e o modelo do Groq ficam como valores padrão configuráveis no `.env`.
- Alternativa considerada: manter `GROQ_API_KEY` e mensagens citando o Groq explicitamente.
- Justificativa: trocar de provedor passa a exigir zero mudança de código — só configuração — e o programa não fica acoplado a um serviço específico.

**8. Terminal → aplicação web em container (3ª etapa)**
- Decisão: camada HTTP com Flask (formulário único, sem JavaScript) servida por gunicorn em `0.0.0.0:8000` dentro de container Docker (`python:3.12-slim`, usuário não-root, HEALTHCHECK).
- Alternativa consideradas: FastAPI (+uvicorn/pydantic — peso e conceito além do escopo do P0) e SDK OpenAI no cliente (reescreveria o módulo testado; o formato da requisição já é compatível com OpenAI via `requests`).
- Justificativa: dentro do container não há terminal, e a plataforma exige que a aplicação escute em `0.0.0.0`; Flask mantém o projeto pequeno, e a lógica de negócio dos módulos permaneceu intacta — só a casca de interação trocou.

**9. TLS do endpoint interno com verificação desligada por padrão**
- Decisão: `IA_TLS_VERIFY=0` como padrão (`requests` com `verify=False`) e tratamento dedicado ao erro de certificado, com mensagem sugerindo a reativação da verificação em provedores públicos.
- Alternativa considerada: manter verificação ligada e exigir instalação do certificado interno do ambiente na imagem.
- Justificativa: o manual do ambiente indica explicitamente o `verify=False` para o endpoint interno (certificado próprio, sem cadeia pública); sem isso, toda chamada falharia com `SSLCertVerificationError`. A flag mantém a verificação religável quando o provedor tem TLS público (ex.: Groq), e a exceção específica evita que o erro apareça como "falha de comunicação" genérica.

## Testes e resultados

Testes **reais** (usam o serviço de verdade) e **simulados** (falhas fabricadas em memória, sem rede — distinção exigida pela especificação do Intermediário).

| Teste | Entrada ou situação | Resultado esperado | Resultado obtido |
|---|---|---|---|
| Reclamação (real) | "Comprei um produto e ele chegou quebrado. Já mandei três e-mails e ninguém responde. Quero meu dinheiro de volta!" | RECLAMAÇÃO | RECLAMAÇÃO ✓ |
| Dúvida (real) | "Vocês têm esse produto na cor azul? E qual o prazo de entrega para o CEP 01234-567?" | DÚVIDA | DÚVIDA ✓ |
| Credencial ausente (real) | Executar em pasta sem `.env` | Mensagem clara, sem chamar a API | "Credencial ausente: defina IA_API_KEY no arquivo .env..." ✓ |
| Credencial inválida (real) | Chave falsa no `.env` → HTTP 401 real do serviço | Mensagem clara, sem expor segredo | "Credencial inválida: o provedor de IA recusou a chave" ✓ |
| Entrada vazia (real) | Enter duas vezes seguidas | Alerta na 1ª tentativa; encerramento controlado na 2ª | "Nenhuma mensagem foi fornecida após duas tentativas." ✓ |
| Timeout (simulado) | Resposta do provedor não chega no prazo | `ErroComunicacao` com mensagem amigável | ✓ |
| Falha de rede (simulado) | Conexão recusada | `ErroComunicacao` com mensagem amigável | ✓ |
| Serviço fora do ar (simulado) | HTTP 503 | `ErroServicoIndisponivel` com mensagem amigável | ✓ |
| Limite de uso (simulado) | HTTP 429 | `ErroServicoIndisponivel` (aguarde e tente novamente) | ✓ |
| JSON inesperado (simulado) | Corpo sem a estrutura esperada | `ErroRespostaInvalida` | ✓ |
| Resposta vazia (simulado) | `content` vazio (tokens consumidos pelo raciocínio) | `ErroRespostaInvalida` | ✓ |
| Categoria inexistente (simulado) | Modelo responde "talvez" | `ErroRespostaInvalida` | ✓ |
| Normalização (simulado) | Modelo responde "  Reclamacao  " | categoria validada como `reclamacao` | ✓ |
| Suíte automatizada (`pytest`, 32 testes) | Prompt, configuração, cliente simulado e rotas web — sem rede | 32/32 verdes | 32 passed in 0.28s ✓ |
| Container: formulário (real) | `GET /` no container rodando | página com o formulário | HTTP 200, título correto ✓ |
| Container: classificação (real) | `POST /` com reclamação, container apontado ao Groq | categoria na página | "Categoria: RECLAMAÇÃO" ✓ |
| Container: health (real) | `GET /health` no container | status ok | `{"status":"ok"}` HTTP 200 ✓ |
| Container: sem credencial (real) | Container iniciado sem `IA_API_KEY` | mensagem amigável, sem segredo na resposta | "Credencial ausente..." HTTP 502, sem credencial no HTML ✓ |
| Container: logs limpos (real) | `docker logs` após uso | requisições sem conteúdo nem segredo | apenas linhas INFO do gunicorn ✓ |

## Falhas e limitações

**1. O modelo indicado pela documentação não existia mais (Básico — tratado).**

- **O que aconteceu:** a primeira chamada de teste ao Groq retornou 404 (`model_not_found`) para o `llama-3.1-8b-instant`.
- **Como foi identificado:** com uma chamada real antes de escrever o código; o código 404 (e não 401) mostrou que a autenticação estava correta e o problema era o catálogo de modelos.
- **Como foi tratado:** listagem dos modelos disponíveis na conta (`GET /models`), migração para o `openai/gpt-oss-20b` e nova chamada de teste — que revelou ainda o comportamento de raciocínio do modelo e levou ao ajuste do `max_tokens`.
- **Por que permanece:** o catálogo de modelos do provedor muda de forma independente do projeto. A partir do Intermediário, o modelo virou configuração (`IA_MODEL` no `.env`): trocar de modelo não exige mais tocar no código.

**2. Erros genéricos com traceback técnico (Básico → tratado no Intermediário).**

- **O que aconteceu:** no Básico, qualquer falha HTTP encerrava o programa com `Erro HTTP <status>: <corpo da resposta>` — técnico e pouco útil.
- **Como foi identificado:** na revisão do enunciado do Intermediário, que exige mensagens compreensíveis e proíbe encerrar com erro técnico extenso.
- **Como foi tratado:** hierarquia de seis exceções próprias, mapeamento de códigos HTTP e exceções de rede para tipos de erro, e tradução para mensagens amigáveis com sugestão no ponto de entrada; traceback disponível apenas com `IA_DEBUG=1`.
- **Por que permanece:** não permanece — foi o objetivo central do Intermediário e está coberto pelos 13 testes acima.

**3. O certificado interno quebraria toda chamada ao LLM (3ª etapa — tratado).**

- **O que aconteceu:** o endpoint interno (`llm-internal.softex:9001`) usa certificado próprio, sem cadeia pública; com verificação TLS padrão, toda chamada falharia com `SSLCertVerificationError` — e, se tratado genericamente, pareceria "falha de comunicação" sem explicação.
- **Como foi identificado:** na leitura do manual do ambiente e na conferência do comportamento do `requests` com endpoints internos.
- **Como foi tratado:** verificação TLS controlada pela flag `IA_TLS_VERIFY` (padrão `0`, conforme o manual) e tratamento dedicado ao erro de SSL, com mensagem que distingue o problema do certificado e sugere a flag — incluindo caso o usuário a reative contra um provedor público.
- **Por que permanece:** a verificação desligada é escolha deliberada para o ambiente interno (como o manual orienta); o risco de MITM é mitigado pelo isolamento da rede interna. Para provedores públicos, `IA_TLS_VERIFY=1` reativa a verificação.

**4. Limitações aceitas do escopo.**

- A validação de credencial inválida depende do provedor responder 401/403; provedores com outro comportamento exigiriam ajuste no mapa de códigos HTTP.
- A suíte automatizada cobre a lógica local (prompt, config, cliente com falhas simuladas, rotas web); um teste de integração contra o endpoint interno real só é possível de dentro da rede do ambiente — validação feita por execução manual após o upload.
- Uma única mensagem por requisição: o programa classifica e responde, sem histórico de conversa (fora do escopo do P0).

## Uso de IA no desenvolvimento

- **Ferramenta utilizada:** Hermes Agent, agente de IA configurado com skills de estudo e de desenvolvimento de software, operando sobre o repositório com a persona de mentor do DIO Agent.
- **Tarefa delegada:** criação da aula de mecanismo (API REST, parâmetros, estrutura de prompt, tipos de erro); estruturação do projeto; escrita do código inicial (`src/main.py`); execução dos testes; operações de Git/GitHub (branch, PR, tag, release) e elaboração deste relatório. Na 3ª etapa: aplicação web (Flask), Dockerfile, suíte `pytest` e build/testes da imagem no Docker local.
- **Resultado aproveitado:** a aula como base conceitual; o código e o README como estrutura inicial; a suíte de testes executada com saída registrada; imagem Docker construída e validada dentro do container.
- **Correções e alterações realizadas:** o modelo indicado pela aula foi trocado após o teste real (404); o `max_tokens` foi corrigido ao observar o comportamento do modelo de raciocínio; os materiais do curso foram mantidos fora do repositório público; no Intermediário, o desenho de módulos e a hierarquia de exceções foram discutidos e aprovados com o autor antes da implementação, e as mensagens foram genericizadas para "provedor de IA" a pedido do autor; na 3ª etapa, padrões apontados ao LLM interno e TLS sem verificação por padrão, conforme decisão do autor e manual do ambiente.
- **Forma de verificação:** execução real de cenários de sucesso e falha em todos os níveis (incluindo HTTP 401 autêntico e classificação real dentro do container via Groq); suíte automatizada de 32 testes sem rede; operações Git verificadas no remoto (`git ls-remote`, `gh pr view`); imagem conferida (`docker images`, ausência do `.env` na imagem, logs sem segredos). Regra adotada: todo o código entregue pode ser explicado pelo autor.

## Reflexão final

- **Principal aprendizado:** "funciona na minha máquina" não é entrega — e a documentação do provedor não é verdade imutável: catálogo e comportamento do modelo precisam ser confirmados com chamadas reais antes de codar. A jornada somou três lições de projeto: separar *detectar* um erro de *explicá-lo*; isolar a lógica de negócio da casca de interação (o terminal virou web sem tocar nos módulos); e a entrega final é um ambiente (imagem), não só um programa — com configuração, saúde e limites próprios.
- **Competência mais desenvolvida:** C04 (ambiente funcional e reprodutível) — a validação aconteceu em um ambiente genuinamente limpo: a imagem foi construída do zero, a aplicação testada dentro do container e a entrega empacotada para execução por terceiros em outra rede.
- **Aspecto a aprimorar:** um teste de integração contra o endpoint interno real (possível apenas de dentro da rede do ambiente) e a evolução da suíte para cenários de carga/uso concorrente do gunicorn.
