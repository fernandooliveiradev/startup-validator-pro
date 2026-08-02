# Startup Validator Pro

Valida ideias de startup usando **DeepSeek V4** (raciocínio + pensamento estruturado) e **Tavily** para pesquisa de mercado e concorrentes.

## Funcionalidades

- 🤖 **DeepSeek V4** (`deepseek-v4-flash`) com `reasoning_effort` e modo *thinking* habilitados, e **fallback automático** para `deepseek-v4-pro`.
- 🔍 **Tavily** para buscar dados reais de mercado e concorrentes antes de responder.
- ⚡ **Streaming** no terminal: raciocínio, chamadas de ferramenta e relatório são exibidos em tempo real.
- 🧠 **Saída estruturada** com score de viabilidade, nível de risco, CAC estimado, MVP mínimo, próximos passos e fontes.
- 🗂️ **Verticais especializadas**: SaaS, E-commerce, Foodtech, IA, Marketplace e Fintech.
- 🔄 **Refinamento iterativo**: refina a ideia em rodadas com base nos pontos fracos.
- 🎬 **Pitch Deck Review**: avalia um pitch como um investidor-anjo.
- ⚖️ **Comparativo**: ranqueia ideias do histórico da mais para a menos promissora.
- 🗄️ **Histórico persistido** em SQLite, com cache para não re-validar a mesma ideia.
- 📤 **Exportação** em Markdown ou JSON.
- 🎨 **CLI interativo** com Rich.

## Requisitos

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/)

## Como usar

```bash
# 1. Instalar dependências
uv sync

# 2. Configurar as chaves de API
cp .env.example .env
# preencha DEEPSEEK_API_KEY e TAVILY_API_KEY no .env

# 3. Executar o app interativo
uv run python main.py
# ou (via entrypoint instalado)
uv run startup-validator
```

## Menu interativo

| Opção | Ação                                              |
|-------|---------------------------------------------------|
| `1`   | Validar nova ideia de startup                     |
| `2`   | Validar com refinamento iterativo                 |
| `3`   | Pitch Deck Review                                 |
| `4`   | Ver histórico de validações                       |
| `5`   | Ver relatório completo de uma validação           |
| `6`   | Comparar ideias do histórico                      |
| `7`   | Exportar validação (Markdown/JSON)                |
| `8`   | Sair                                              |

## Configuração (.env)

| Variável            | Padrão               | Obrigatória | Descrição                     |
|---------------------|----------------------|:-----------:|-------------------------------|
| `DEEPSEEK_API_KEY`  | —                    | ✅           | Chave da API DeepSeek         |
| `TAVILY_API_KEY`    | —                    | ✅           | Chave da API Tavily           |
| `MODEL_ID`          | `deepseek-v4-flash`  | ❌           | Modelo DeepSeek               |
| `FALLBACK_MODEL_ID` | `deepseek-v4-pro`    | ❌           | Modelo de fallback            |
| `REASONING_EFFORT`  | `high`               | ❌           | Esforço de raciocínio         |
| `THINKING_ENABLED`  | `true`               | ❌           | Habilita o modo "thinking"    |
| `MAX_TOKENS`        | `8192`               | ❌           | Limite de tokens de saída     |

## Testes

```bash
uv run pytest
```

## Estrutura

```
src/startup_validator/
├── __init__.py    # metadados do pacote
├── config.py      # variáveis de ambiente e configuração
├── schemas.py     # modelos Pydantic de resposta
├── agent.py       # agente DeepSeek + tool Tavily
├── services.py    # cache, refinamento, comparativo, exportação, streaming
├── stream.py      # renderização em tempo real (Rich Live)
├── verticals.py   # templates de análise por vertical
├── history.py     # histórico de validações
├── db.py          # persistência SQLite (agno)
├── ui.py          # interface Rich
└── cli.py         # loop interativo
```

## Licença

Licenciado sob a [MIT License](LICENSE).
