# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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
