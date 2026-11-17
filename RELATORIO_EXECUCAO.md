# Relatório de Execução — P0 Primeiro Fluxo LLM

**Projeto:** Classificador de mensagens de atendimento (dúvida, reclamação ou elogio)
**Repositório:** https://github.com/codedilton/p0-primeiro-fluxo-llm
**Estado:** níveis Básico e Intermediário concluídos e lançados (tags `p0-basico` e `p0-intermediario`). Este relatório será incrementado a cada nível concluído.

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

### Avançado — pendente

Previsto: testes automatizados, `.env.example`, documento de decisões e validação da reprodutibilidade. Branch e pull request já praticados desde o Básico.

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

**3. Limitações aceitas do escopo.**

- A validação de credencial inválida depende do provedor responder 401/403; provedores com outro comportamento exigiriam ajuste no mapa de códigos HTTP.
- Os testes simulados foram executados como bateria manual na sessão de desenvolvimento; virar suíte automatizada (`pytest`) é meta do Avançado.
- Uma única mensagem por execução: o programa classifica e encerra. Diálogo contínuo ficaria fora do escopo do P0.

## Uso de IA no desenvolvimento

- **Ferramenta utilizada:** Hermes Agent, agente de IA configurado com skills de estudo e de desenvolvimento de software, operando sobre o repositório com a persona de mentor do DIO Agent.
- **Tarefa delegada:** criação da aula de mecanismo (API REST, parâmetros, estrutura de prompt, tipos de erro); estruturação do projeto; escrita do código inicial (`src/main.py`); execução dos testes; operações de Git/GitHub (branch, PR, tag, release) e elaboração deste relatório.
- **Resultado aproveitado:** a aula como base conceitual; o código e o README como estrutura inicial; a suíte de testes manuais executada com saída registrada.
- **Correções e alterações realizadas:** o modelo indicado pela aula foi trocado após o teste real (404); o `max_tokens` foi corrigido ao observar o comportamento do modelo de raciocínio; os materiais do curso foram mantidos fora do repositório público; no Intermediário, o desenho de módulos e a hierarquia de exceções foram discutidos e aprovados com o autor antes da implementação, e as mensagens foram genericizadas para "provedor de IA" a pedido do autor.
- **Forma de verificação:** todo resultado conferido com execução real (5 cenários com serviço de verdade, incluindo um HTTP 401 autêntico) e com bateria simulada de 8 cenários sem rede; operações Git verificadas no remoto (`git ls-remote`, `gh pr view`). Regra adotada: todo o código entregue pode ser explicado pelo autor.

## Reflexão final

- **Principal aprendizado:** "funciona na minha máquina" não é entrega — e a documentação do provedor não é verdade imutável: catálogo e comportamento do modelo precisam ser confirmados com chamadas reais antes de codar. No Intermediário, somou-se a lição de projeto: separar *detectar* um erro de *explicá-lo* deixa o programa mais fácil de testar e mais gentil com quem usa.
- **Competência mais desenvolvida:** C03 (integração com APIs REST) — montar requisição, ler código de status, interpretar a estrutura da resposta e converter cada falha em um tipo de erro próprio, com credencial ausente e inválida demonstradas em testes reais.
- **Aspecto a aprimorar:** os testes simulados ainda são bateria manual — virar suíte automatizada executável com um comando é a meta do Avançado, junto com a validação da entrega em ambiente limpo.
