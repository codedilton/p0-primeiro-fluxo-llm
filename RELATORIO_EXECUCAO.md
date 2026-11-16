# Relatório de Execução — P0 Primeiro Fluxo LLM

**Projeto:** Classificador de mensagens de atendimento (dúvida, reclamação ou elogio)
**Repositório:** https://github.com/codedilton/p0-primeiro-fluxo-llm
**Estado:** nível Básico concluído e lançado (tag `p0-basico`). Este relatório será incrementado a cada nível concluído.

## Evolução por nível

### Básico — concluído

- Núcleo funcional completo: lê a mensagem no terminal, envia à API do LLM (Groq, endpoint compatível com OpenAI) e exibe a categoria validada.
- Chave de API fora do código: lida da variável de ambiente `GROQ_API_KEY`, com `.gitignore` protegendo o `.env` desde o primeiro commit.
- Dependências declaradas (`requirements.txt`) e README que permite a outra pessoa instalar, configurar e executar sem ajuda.
- Fluxo de Git praticado desde o primeiro marco: branch `feature/nucleo-basico`, pull request #1 e tag `p0-basico`.

### Intermediário — pendente

Previsto: separação do código em funções de responsabilidade única (entrada, prompt, chamada, tratamento, saída) e tratamento específico dos seis tipos de erro (configuração, autenticação, comunicação, indisponibilidade, entrada e resposta).

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

## Testes e resultados

| Teste | Entrada ou situação | Resultado esperado | Resultado obtido |
|---|---|---|---|
| Reclamação | "Comprei um produto e ele chegou quebrado. Já mandei três e-mails e ninguém responde. Quero meu dinheiro de volta!" | RECLAMAÇÃO | RECLAMAÇÃO ✓ |
| Elogio | "Gostaria de registrar meu agradecimento pelo atendimento de vocês, foi fantástico, resolveu tudo rápido!" | ELOGIO | ELOGIO ✓ |
| Dúvida | "Vocês têm esse produto na cor azul? E qual o prazo de entrega para o CEP 01234-567?" | DÚVIDA | DÚVIDA ✓ |
| Entrada vazia | Enter sem digitar nada | Mensagem clara, sem chamar a API | "Forneça um texto válido: a mensagem não pode ser vazia." ✓ |
| Sem credencial | Executar sem `GROQ_API_KEY` definida | Mensagem clara, sem chamar a API | "Defina a variável GROQ_API_KEY no ambiente..." ✓ |

## Falhas e limitações

**O modelo indicado pela documentação não existia mais.**

- **O que aconteceu:** a primeira chamada de teste ao Groq retornou 404 (`model_not_found`) para o `llama-3.1-8b-instant`.
- **Como foi identificado:** com uma chamada real antes de escrever o código; o código 404 (e não 401) mostrou que a autenticação estava correta e o problema era o catálogo de modelos.
- **Como foi tratado:** listagem dos modelos disponíveis na conta (`GET /models`), migração para o `openai/gpt-oss-20b` e nova chamada de teste — que revelou ainda o comportamento de raciocínio do modelo e levou ao ajuste do `max_tokens`.
- **Por que permanece:** o catálogo de modelos do provedor muda de forma independente do projeto, e o programa não detecta dinamicamente os modelos disponíveis (fora do escopo). Além disso, o tratamento de erros HTTP ainda é genérico (exibe status e texto da resposta) — o refinamento por tipo de erro é exatamente o objetivo do nível Intermediário.

## Uso de IA no desenvolvimento

- **Ferramenta utilizada:** Hermes Agent, agente de IA configurado com skills de estudo e de desenvolvimento de software, operando sobre o repositório com a persona de mentor do DIO Agent.
- **Tarefa delegada:** criação da aula de mecanismo (API REST, parâmetros, estrutura de prompt, tipos de erro); estruturação do projeto; escrita do código inicial (`src/main.py`); execução dos testes; operações de Git/GitHub (branch, PR, tag, release) e elaboração deste relatório.
- **Resultado aproveitado:** a aula como base conceitual; o código e o README como estrutura inicial; a suíte de testes manuais executada com saída registrada.
- **Correções e alterações realizadas:** o modelo indicado pela aula foi trocado após o teste real (404); o `max_tokens` foi corrigido ao observar o comportamento do modelo de raciocínio; os materiais do curso foram mantidos fora do repositório público.
- **Forma de verificação:** todo resultado conferido com execução real (cinco cenários de teste com saída no terminal) e com verificação no remoto (`git ls-remote`, `gh pr view`). Regra adotada: todo o código entregue pode ser explicado pelo autor.

## Reflexão final

- **Principal aprendizado:** "funciona na minha máquina" não é entrega — e a documentação do provedor não é verdade imutável: catálogo e comportamento do modelo precisam ser confirmados com chamadas reais antes de codar.
- **Competência mais desenvolvida:** C03 (integração com APIs REST) — montar requisição, ler código de status e interpretar a estrutura da resposta passou de conceito para prática.
- **Aspecto a aprimorar:** o tratamento de erros ainda é genérico (refino previsto para o Intermediário) e os testes são manuais — automatizá-los é a meta do Avançado.
