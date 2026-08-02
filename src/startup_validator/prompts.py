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

# Instruções do agente estruturado (produz relatório no formato DetailedValidation).
AGENTE_ESTRUTURADO_INSTRUCOES = [
    INVESTIDOR_PERSONA,
    USAR_TAVILY,
    "Responda exclusivamente no formato estruturado solicitado, em português.",
    "Seja objetivo, com argumentos claros e recomendações acionáveis.",
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
    "O usuário descreveu a ideia de startup abaixo em texto. Revise como um "
    "investidor-anjo avaliaria esse pitch: aponte forças, falhas, lacunas e o "
    "que faltaria para investir.\n\nDescrição: {ideia}"
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
 3. Pitch Deck Review   → avalia a sua descrição como se fosse um pitch para um
                          investidor: forças, falhas e o que faltaria para investir.

[bold]Opções de gerenciamento:[/bold]
 4. Ver histórico       → lista as validações salvas (ID, data e ideia).
 5. Ver relatório       → mostra o relatório completo de uma validação salva.
 6. Comparar ideias     → escolhe 2+ validações do histórico e ranqueia qual é
                          a mais promissora.
 7. Exportar            → salva uma validação em Markdown ou JSON.

[bold]Dica:[/bold] ao validar, escolha uma vertical (SaaS, E-commerce, Foodtech, IA,
Marketplace ou Fintech) para uma análise mais especializada. Use 0 para Geral.
"""
