# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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
