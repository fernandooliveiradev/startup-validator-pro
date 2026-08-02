"""Centralização de todos os prompts e instruções do agente.

Manter todos os textos em um só lugar evita hardcode espalhado no código
e facilita ajustes de tom/conteúdo sem tocar na lógica.
"""

# --- Instruções (system prompt) ---

INVESTIDOR_PERSONA = "Você é um investidor-anjo sênior e brutalmente honesto."
USAR_TAVILY = (
    "Sempre use a ferramenta Tavily para buscar dados REAIS de mercado "
    "e concorrentes antes de responder."
)

# Exemplo do JSON que o modelo deve produzir (orienta o DeepSeek, que usa
# response_format={'type':'json_object'} e exige a palavra "json" + exemplo).
JSON_MODE_EXEMPLO = """
Responda APENAS com um objeto JSON válido, sem texto antes ou depois, seguindo
exatamente este formato (substitua os valores de exemplo):

{
  "resumo": "Resumo objetivo da ideia.",
  "pontos_fortes": ["Vantagem 1", "Vantagem 2"],
  "pontos_fracos": ["Risco 1", "Risco 2"],
  "analise_mercado": "Análise de mercado com dados reais pesquisados.",
  "score": 70,
  "nivel_risco": "médio",
  "cac_estimado": "R$ 100-200 por cliente",
  "mvp_minimo": "O que construir e como validar.",
  "proximos_passos": ["Ação 1", "Ação 2"],
  "referencias": ["https://fonte1", "https://fonte2"]
}
"""

# Instruções do agente estruturado (produz relatório no formato DetailedValidation).
AGENTE_ESTRUTURADO_INSTRUCOES = [
    INVESTIDOR_PERSONA,
    USAR_TAVILY,
    "Responda exclusivamente no formato estruturado solicitado, em português.",
    "Seja objetivo, com argumentos claros e recomendações acionáveis.",
    JSON_MODE_EXEMPLO,
]

# Instruções do agente de texto livre (comentário/avaliação em texto corrido).
AGENTE_TEXTO_LIVRE_INSTRUCOES = [
    INVESTIDOR_PERSONA,
    USAR_TAVILY,
    "Responda em português, em texto corrido e bem estruturado.",
    "Seja objetivo e acionável.",
]


# --- Prompts de ação ---

VALIDAR_IDEIA_TEMPLATE = (
    "Valide esta ideia de startup: {ideia}. Pesquise mercado e concorrentes."
)

PITCH_REVIEW_TEMPLATE = (
    "Abaixo está o relatório de validação de uma ideia de startup, já analisado "
    "por um investidor. Faça uma avaliação de PITCH DECK a partir desse conteúdo, "
    "cobrindo os seguintes pilares:\n\n"
    "1. CLAREZA DA PROPOSTA DE VALOR — o problema e a solução ficam claros em "
    "poucos segundos?\n"
    "2. COERÊNCIA DO MODELO DE NEGÓCIOS — a monetização, o mercado (TAM/SAM/SOM) "
    "e as projeções são realistas e atraentes?\n"
    "3. ESTRUTURA E STORYTELLING — a narrativa (problema, solução, tração, equipe, "
    "mercado, pedido de investimento) flui de forma convincente?\n"
    "4. DESIGN E IMPACTO VISUAL — identidade visual transmite profissionalismo, "
    "sem excesso de texto ou poluição?\n"
    "5. ALINHAMENTO COM O INVESTIDOR — quais perguntas difíceis os fundos de VC ou "
    "investidores-anjo fariam, e como os fundadores devem respondê-las?\n\n"
    "Para cada pilar: aponte o que está bom, o que está fraco e como melhorar. "
    "Termine com um checklist objetivo do que falta para o pitch atrair "
    "investimento.\n\n"
    "Conteúdo da validação:\n{relatorio}"
)

REFINAR_FEEDBACK_TEMPLATE = (
    "{ideia}\n\n[Refinamento] Com base nos pontos fracos apontados abaixo, "
    "apresente uma versão ajustada e melhor da ideia:\n{feedback}"
)

COMPARAR_IDEAS_TEMPLATE = (
    "Compare as seguintes ideias de startup e ranqueie da mais para a menos "
    "promissora, justificando cada posição com base em mercado, moat, "
    "dificuldade e unidade econômica:\n\n{ideias}\n\n"
    "Responda em português, em formato de lista ordenada com argumentos claros."
)


# --- Descrições de ajuda por comando ---

HELP_TEXT = """[bold cyan]O que este app faz[/bold cyan]

Você descreve uma ideia de startup e o agente de IA pesquisa o mercado real
e avalia a viabilidade como um investidor-anjo. Tudo fica salvo no histórico.

[bold]Opções de criação:[/bold]
 1. Validar ideia       → gera um relatório estruturado (score, pontos fortes/fracos,
                          análise de mercado, CAC, MVP, próximos passos e fontes).
 2. Refinar ideia       → valida e, em rodadas, melhora a ideia com base nos
                          pontos fracos apontados.
 3. Pitch Deck Review   → escolhe uma validação já salva e a avalia como um pitch
                          para investidor: clareza, modelo de negócio, storytelling,
                          design e alinhamento com o investidor.

[bold]Opções de gerenciamento:[/bold]
 4. Ver histórico       → lista as validações salvas (ID, data e ideia).
 5. Ver relatório       → mostra o relatório completo de uma validação salva.
 6. Comparar ideias     → escolhe 2+ validações do histórico e ranqueia qual é
                          a mais promissora.
 7. Exportar            → salva uma validação em Markdown, JSON ou HTML.

[bold]Dica:[/bold] ao validar, escolha uma vertical (SaaS, E-commerce, Foodtech, IA,
Marketplace ou Fintech) para uma análise mais especializada. Use 0 para Geral.
"""
