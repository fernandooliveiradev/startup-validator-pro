# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [3.3.2] — 2026-08-02

### Alterado

- Artefato HTML do relatório estruturado agora é um **dashboard profissional**:
  gauge de score (SVG), cards de indicadores (risco, CAC, MVP) e listas com
  **ícones SVG (Lucide via CDN)** em vez de emojis.
- Ícones Lucide em todo o layout (cabeçalho, seções, rodapé, botão de tema).

## [3.3.1] — 2026-08-02

### Adicionado

- Artefato HTML também para **Ver Relatório** (opção 5).
- **Exportar** (opção 7) agora aceita o formato **HTML** além de Markdown/JSON.

## [3.3.0] — 2026-08-02

### Adicionado

- **Artefatos HTML** (Tailwind CSS via CDN) com **tema claro e escuro** (quase preto) e toggle.
- Ao final de cada saída (validação, refinamento, pitch deck review e comparativo), o app
  pergunta se o usuário quer gerar o artefato HTML; se sim, mostra o caminho ou abre no navegador.
- Módulo `artifacts.py` com geração segura de HTML (escape de conteúdo) e Markdown → HTML básico.

## [3.2.2] — 2026-08-02

### Alterado

- **Pitch Deck Review** agora analisa uma **validação já salva** no histórico (selecionada
  pelo ID), em vez de solicitar uma nova ideia em texto.
- O prompt de avaliação cobre os **5 pilares**: clareza da proposta de valor, coerência do
  modelo de negócios (TAM/SAM/SOM), estrutura e storytelling, design e impacto visual, e
  alinhamento com o investidor (perguntas difíceis que fundos fazem).

## [3.2.1] — 2026-08-02

### Corrigido

- **Bug grave no dispatcher do menu**: as opções `1` (Validar), `2` (Refinar) e `6` (Comparar)
  eram chamadas sem o argumento `agent`, lançando `TypeError` na execução. Agora o dispatch
  repassa `agent` corretamente aos handlers que o exigem.
- Teste de regressão adicionado (`test_cli.py`) para garantir que cada handler recebe os
  argumentos certos.

## [3.2.0] — 2026-08-02

### Adicionado

- **Ajuda integrada** (opção `0` no menu): explica o que o app faz e o que cada ação produz.
- Menu organizado em **seções** (`Criar`, `Gerenciar`, `Sistema`) para facilitar a navegação.
- Módulo `prompts.py` centraliza todos os prompts e instruções (elimina hardcode espalhado).
- Módulo `commands.py` isola o handler de cada comando do menu.
- Testes novos para `prompts` e para o streaming unificado.

### Alterado

- **Streaming unificado**: `stream_run` substitui `stream_validation`/`stream_free_text` com um gerador único parametrizado por parser (elimina ~80% de duplicação).
- **Renderer unificado**: `render_stream(..., structured=bool)` substitui `render_stream`/`render_free_text`.
- `cli.py` virou um **dispatcher fino** que mapeia opção -> handler, sem lógica de negócio no loop.
- `agent.py` documenta a regra de qual agente usar (estruturado vs. texto livre) e usa `prompts.py`.
- `ui.py` sem código morto (`ask_compare_count`, `print_idea_list`, etc. removidos).

## [3.1.1] — 2026-08-02

### Corrigido

- **Refinamento iterativo quebrava quando o parsing do schema falhava**: `_validate_once`
  agora usa estratégias múltiplas de parse (objeto, dict, JSON bruto e fallback pelas
  mensagens da sessão) em vez de apenas exigir o objeto `DetailedValidation`.
- **Pitch Deck Review travava** esperando um modelo estruturado que o DeepSeek nem sempre
  produz: agora usa um agente de texto livre com streaming que sempre termina, e gera
  resposta em texto corrido.

### Alterado

- README reescrito em português focado em tech recruiters: o que é, por que agno,
  arquitetura do agente e como rodar no desktop.

## [3.1.0] — 2026-08-02

### Adicionado

- **Streaming** no terminal: raciocínio, chamadas de ferramenta (Tavily) e relatório exibidos
  em tempo real via Rich `Live`.
- **Fallback automático de modelo**: em falha, troca de `deepseek-v4-flash` para `deepseek-v4-pro`.
- **Saída estruturada ampliada**: `score`, `nivel_risco`, `cac_estimado`, `mvp_minimo`,
  `proximos_passos` e `referencias` no schema.
- **Verticais especializadas** (`verticals.py`): SaaS, E-commerce, Foodtech, IA, Marketplace e Fintech.
- **Refinamento iterativo**: refina a ideia em rodadas com base nos pontos fracos.
- **Pitch Deck Review**: avaliação de pitch no papel de investidor-anjo.
- **Comparativo de ideias**: ranqueia validações do histórico da mais para a menos promissora.
- **Cache de validação**: evita re-validar ideias já analisadas (match fuzzy por resumo).
- **Exportação** de relatório em Markdown ou JSON.
- **Testes unitários** (pytest) para `schemas`, `services` e `verticals`.
- Variável de configuração `MAX_TOKENS` e `FALLBACK_MODEL_ID`.

### Alterado

- Menu expandido para 8 opções.

### Adicionado (08-01)

- Nova opção no menu para visualizar o **relatório completo** de uma validação
  salva no histórico (reconstruído a partir do JSON persistido).
- Licença **MIT** (`LICENSE`) e metadados correspondentes no `pyproject.toml`.

### Removido (08-01)

- Aviso de segurança sobre o `.env` no README.

## [3.0.0] — 2026-08-01

### Adicionado

- Reestruturação em pacote `src/startup_validator` com separação de responsabilidades:
  `config`, `schemas`, `agent`, `db`, `history`, `ui`, `cli`.
- Integração com **DeepSeek V4** (`deepseek-v4-flash`) via provider nativo do agno,
  com `reasoning_effort` e modo *thinking* habilitados.
- Historico de validações agora mostra também a ideia validada (antes só ID e data).
- Entrypoint de console instalável: `uv run startup-validator`.
- Variáveis de configuração: `MODEL_ID`, `REASONING_EFFORT`, `THINKING_ENABLED`.

### Corrigido

- Chaves de API ausentes no topo do módulo derrubavam o processo no momento do import;
  a validação agora acontece apenas na execução do CLI.
- `tmp/workflows.db` (binário de runtime) era versionado no git; removido e coberto
  pelo `.gitignore` (junto de `tmp/`, `*.db`, `.env`).
- Dependências "fantasma" não utilizadas (`fastapi`, `uvicorn`, `aiosqlite`) removidas;
  dependências faltantes (`rich`, `pydantic`, `dotenv`) declaradas corretamente via
  extras do agno (`sqlite`, `openai`, `tavily`).
- Encoding/emojis no console Windows.
- `README.md` e `pyproject.toml` com descrições reais (antes placeholders/duplicados).

### Removido

- Sobrecarga de `Workflow` de etapa única, substituído por `Agent` simples com
  persistência e saída estruturada.

## [0.1.0] — versão inicial

- Protótipo em `main.py` usando `OpenAIChat(gpt-4o)` e `Workflow`.
