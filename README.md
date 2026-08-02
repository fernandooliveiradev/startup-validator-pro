# 🎓 Startup Validator Pro

**Validação de ideias de startup com IA** — um agente de IA que pesquisa o mercado real e produz um relatório estruturado de viabilidade, no estilo de um investidor-anjo brutalmente honesto.

Este é um **projeto de demonstração de engenharia de software**, escrito em **Python**, que orquestra um *agente de IA* (DeepSeek V4), uma ferramenta de *pesquisa na web* (Tavily) e *persistência local* (SQLite) em um **CLI interativo para desktop**.

---

## 🧠 O que este projeto faz

O usuário digita uma ideia de startup e o agente:

1. **Pesquisa na internet** (Tavily) dados reais de mercado e concorrentes (ex.: tamanho de mercado, principais players, faixas de preço).
2. **Raciocina** com o modelo **DeepSeek V4** (com *thinking* e *reasoning effort* habilitados).
3. **Produz um relatório estruturado** com:
   - Resumo objetivo
   - Pontos fortes e fracos
   - Análise de mercado 2025-2026
   - **Score de viabilidade (0-100)**
   - Nível de risco, CAC estimado, MVP mínimo
   - Próximos passos (30 dias)
   - Fontes pesquisadas
4. **Salva tudo localmente** (SQLite) para histórico e consulta futura.

---

## 🛠️ Stack & por quê

| Tecnologia | Papel | Por que |
|-----------|-------|---------|
| **Python 3.13** | Linguagem | Ecossistema rico em IA/ML e tipagem moderna |
| **agno 2.3** | Framework de agentes | Orquestra o agente, as ferramentas e a persistência de sessões em uma API única |
| **DeepSeek V4** | Modelo de linguagem (LLM) | Motor de raciocínio; API compatível com OpenAI |
| **Tavily** | Ferramenta de pesquisa web | Dá ao agente acesso a dados reais de mercado (evita alucinação) |
| **Pydantic** | Validação de dados | Garante que a resposta do modelo tenha exatamente a estrutura esperada |
| **SQLite** | Persistência | Armazena o histórico de validações |
| **Rich** | Interface de terminal | Renderiza menus, tabelas, painéis e streaming em tempo real |
| **uv** | Gerenciador de projeto/deps | Instala e executa tudo de forma reproduzível |

### Por que **agno** e não só "chamar a API do DeepSeek"?

- **Agentic**: o modelo não só "responde" — ele **decide quando chamar ferramentas** (ex.: pesquisar na web) e orquestra o fluxo inteiro.
- **Saída estruturada**: com `output_schema` (Pydantic), o framework força o LLM a responder no formato exato do relatório, e já converte a resposta em um objeto Python tipado.
- **Persistência embutida**: o próprio framework salva as sessões (mensagens, respostas) no banco, sem que eu tenha que escrever a camada de histórico do zero.
- **Streaming simplificado**: o agno expõe eventos (raciocínio, chamada de ferramenta, deltas de texto), o que permitiu implementar streaming no terminal com pouco código.

---

## 🗂️ Como o agente funciona (arquitetura)

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI interativo (Rich)                  │
│                  menu com 8 opções + streaming              │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                   Agente (agno.Agent)                       │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │  DeepSeek V4 │   │ TavilyTools  │   │ output_schema   │  │
│  │  (LLM)       │   │ (pesquisa)   │   │ (Pydantic)      │  │
│  └──────┬──────┘   └──────────────┘   └─────────────────┘  │
│         │  decide chamar a ferramenta quando precisa        │
└─────────┼──────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│               Persistência (SQLite via agno)               │
│        histórico de validações + respostas salvas          │
└────────────────────────────────────────────────────────────┘
```

**Fluxo de uma validação:**
1. Usuário digita a ideia no CLI.
2. O agente (DeepSeek) entende a tarefa e **chama o Tavily** para pesquisar mercado/concorrentes.
3. Com os dados, o modelo **raciocina** e gera o relatório.
4. O agno **valida a resposta contra o schema** Pydantic e entrega um objeto `DetailedValidation`.
5. O CLI exibe o relatório (com streaming ao vivo) e **salva no SQLite**.

---

## 🚀 Como rodar no desktop

### Pré-requisitos
- **Python 3.13+**
- **uv** (gerenciador de projetos Python) — [instalação oficial](https://docs.astral.sh/uv/)

### Passo a passo

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd startup-validator-pro

# 2. Instale as dependências
uv sync

# 3. Configure as chaves de API
cp .env.example .env
# edite o .env e preencha:
#   DEEPSEEK_API_KEY=sk-...
#   TAVILY_API_KEY=tvly-...

# 4. Rode o app interativo
uv run python main.py
#    ou (entrypoint instalado):
uv run startup-validator
```

### Menu

O menu é organizado em seções. Use `0` para ver a ajuda completa dentro do app.

| Opção | Seção | Ação |
|------|-------|------|
| `1` | Criar | Validar nova ideia (relatório estruturado) |
| `2` | Criar | Validar com refinamento iterativo |
| `3` | Criar | Pitch Deck Review (analisa uma validação salva) |
| `4` | Gerenciar | Ver histórico |
| `5` | Gerenciar | Ver relatório completo |
| `6` | Gerenciar | Comparar ideias |
| `7` | Gerenciar | Exportar (Markdown/JSON) |
| `0` | Sistema | Ajuda |
| `8` | Sistema | Sair |

### Testes

```bash
uv run pytest
```

---

## 🧪 Destaques de engenharia

- **Streaming em tempo real**: raciocínio, chamadas de ferramenta e texto aparecem ao vivo via `Rich.Live`.
- **Fallback de modelo**: se `deepseek-v4-flash` falhar, o sistema tenta automaticamente `deepseek-v4-pro`.
- **Saída estruturada robusta**: o parsing do schema é resiliente a falhas intermitentes do LLM (o sistema tenta múltiplas estratégias de parse antes de desistir).
- **Cache de validação**: ideias parecidas não são re-validadas (match fuzzy por resumo).
- **Verticais especializadas**: instruções diferentes por setor (SaaS, E-commerce, Foodtech, IA, Marketplace, Fintech).
- **Separação de responsabilidades**: código organizado em módulos (`config`, `schemas`, `prompts`, `agent`, `commands`, `services`, `stream`, `history`, `db`, `ui`, `cli`).
- **Zero hardcode e zero duplicação**: prompts centralizados em `prompts.py`; streaming unificado em um único gerador parametrizado; cada comando do menu isolado em `commands.py`.
- **Ajuda integrada**: opção `0` explica o que cada ação faz, direto no terminal.

---

## 📁 Estrutura

```
src/startup_validator/
├── __init__.py    # metadados do pacote
├── config.py      # variáveis de ambiente e configuração
├── schemas.py     # modelos Pydantic de resposta (DetailedValidation)
├── prompts.py     # centralização de prompts e instruções
├── agent.py       # fábrica de agentes (estruturado e texto livre)
├── commands.py    # handlers de cada comando do menu
├── services.py    # cache, refinamento, comparativo, exportação, streaming
├── stream.py      # renderização em tempo real (Rich Live)
├── verticals.py   # templates de análise por vertical
├── history.py     # leitura do histórico de validações
├── db.py          # persistência SQLite (agno)
├── ui.py          # interface Rich (menu em seções, ajuda, prompts)
└── cli.py         # dispatcher fino (loop principal)
```

---

## 📄 Licença

Licenciado sob a [MIT License](LICENSE).
