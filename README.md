# Startup Validator Pro

Valida ideias de startup usando **DeepSeek V4** (raciocínio + pensamento estruturado) e **Tavily** para pesquisa de mercado e concorrentes.

## Funcionalidades

- 🤖 **DeepSeek V4** (`deepseek-v4-flash`) com `reasoning_effort` e modo *thinking* habilitados.
- 🔍 **Tavily** para buscar dados reais de mercado e concorrentes antes de responder.
- 🧠 **Saída estruturada**: relatório em `resumo`, `pontos_fortes`, `pontos_fracos` e `analise_mercado`.
- 🗄️ **Histórico persistido** em SQLite (via agno), com ID, data e a ideia validada.
- 🎨 **CLI interativo** com Rich (menu, tabelas e painéis).

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

> ⚠️ **Nunca commite o `.env`.** Ele está no `.gitignore`. As chaves de API são segredos — rotacione-as se forem expostas.

## Menu interativo

| Opção | Ação                                         |
|-------|----------------------------------------------|
| `1`   | Validar nova ideia de startup                |
| `2`   | Ver histórico de validações                  |
| `3`   | Sair                                         |

## Configuração (.env)

| Variável           | Padrão              | Obrigatória | Descrição                     |
|--------------------|---------------------|:-----------:|-------------------------------|
| `DEEPSEEK_API_KEY` | —                   | ✅           | Chave da API DeepSeek         |
| `TAVILY_API_KEY`   | —                   | ✅           | Chave da API Tavily           |
| `MODEL_ID`         | `deepseek-v4-flash` | ❌           | Modelo DeepSeek               |
| `REASONING_EFFORT` | `high`              | ❌           | Esforço de raciocínio         |
| `THINKING_ENABLED` | `true`              | ❌           | Habilita o modo "thinking"    |

## Estrutura

```
src/startup_validator/
├── __init__.py    # metadados do pacote
├── config.py      # variáveis de ambiente e configuração
├── schemas.py     # modelos Pydantic de resposta
├── agent.py       # agente DeepSeek + tool Tavily
├── db.py          # persistência SQLite (agno)
├── history.py     # histórico de validações
├── ui.py          # interface Rich
└── cli.py         # loop interativo e validação de ambiente
```

## Licença

Privado.
