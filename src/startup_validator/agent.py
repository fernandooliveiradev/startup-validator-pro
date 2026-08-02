"""Fábrica e configuração do agente analista baseado em DeepSeek V4."""

from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.tavily import TavilyTools

from startup_validator import config
from startup_validator.schemas import DetailedValidation

INSTRUCTIONS = [
    "Você é um investidor-anjo sênior e brutalmente honesto.",
    "Sempre use a ferramenta Tavily para buscar dados REAIS de mercado e concorrentes antes de responder.",
    "Responda exclusivamente no formato estruturado solicitado, em português.",
]


def build_model() -> DeepSeek:
    """Constrói o modelo DeepSeek com raciocínio habilitado."""
    extra_body: Dict[str, Any] = {}
    if config.THINKING_ENABLED:
        extra_body["thinking"] = {"type": "enabled"}

    return DeepSeek(
        id=config.MODEL_ID,
        reasoning_effort=config.REASONING_EFFORT,
        extra_body=extra_body or None,
    )


def build_agent(db: Optional[Any] = None) -> Agent:
    """Constrói o agente analista conectado ao banco (se fornecido)."""
    return Agent(
        name="Analista de Startups",
        model=build_model(),
        tools=[TavilyTools()],
        instructions=INSTRUCTIONS,
        output_schema=DetailedValidation,
        db=db,
        markdown=False,
    )
