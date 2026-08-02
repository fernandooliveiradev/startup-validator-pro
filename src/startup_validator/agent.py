"""Fábrica e configuração do agente analista baseado em DeepSeek V4."""

from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.tavily import TavilyTools

from startup_validator import config
from startup_validator.schemas import DetailedValidation
from startup_validator.verticals import get_vertical

BASE_INSTRUCTIONS = [
    "Você é um investidor-anjo sênior e brutalmente honesto.",
    "Sempre use a ferramenta Tavily para buscar dados REAIS de mercado e concorrentes antes de responder.",
    "Responda exclusivamente no formato estruturado solicitado, em português.",
    "Seja objetivo, com argumentos claros e recomendações acionáveis.",
]


def build_model(model_id: Optional[str] = None, max_tokens: Optional[int] = None) -> DeepSeek:
    """Constrói o modelo DeepSeek com raciocínio habilitado."""
    extra_body: Dict[str, Any] = {}
    if config.THINKING_ENABLED:
        extra_body["thinking"] = {"type": "enabled"}

    return DeepSeek(
        id=model_id or config.MODEL_ID,
        reasoning_effort=config.REASONING_EFFORT,
        max_tokens=max_tokens if max_tokens is not None else int(config.MAX_TOKENS),
        extra_body=extra_body or None,
    )


def build_agent(
    db: Optional[Any] = None,
    vertical: Optional[str] = None,
    model_id: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> Agent:
    """Constrói o agente analista conectado ao banco (se fornecido).

    Args:
        db: Banco SQLite (agno) para persistência.
        vertical: Chave da vertical de mercado (ver `verticals.VERTICAIS`).
        model_id: Id do modelo DeepSeek (permite fallback explícito).
        max_tokens: Limite de tokens de saída.
    """
    instrucoes = list(BASE_INSTRUCTIONS)
    if vertical:
        v = get_vertical(vertical)
        instrucoes.extend(v.instrucoes)

    return Agent(
        name="Analista de Startups",
        model=build_model(model_id=model_id, max_tokens=max_tokens),
        tools=[TavilyTools()],
        instructions=instrucoes,
        output_schema=DetailedValidation,
        db=db,
        markdown=False,
        stream=True,
    )
