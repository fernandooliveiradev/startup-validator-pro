"""Fábrica de agentes baseados em DeepSeek V4.

Regra de uso:
- `build_agent`: agente **estruturado** (produz `DetailedValidation`), conectado
  ao banco para persistência e cache. Use para validar e refinar ideias.
- `build_free_text_agent`: agente de **texto livre** (sem schema), para
  avaliações em texto corrido (pitch review, comparativo).
"""

from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.tavily import TavilyTools

from startup_validator import config, prompts
from startup_validator.schemas import DetailedValidation
from startup_validator.verticals import get_vertical


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


def _base_kwargs(
    db: Optional[Any] = None,
    model_id: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> dict:
    """Argumentos comuns a todos os agentes."""
    return {
        "model": build_model(model_id=model_id, max_tokens=max_tokens),
        "tools": [TavilyTools()],
        "db": db,
        "markdown": False,
    }


def build_agent(
    db: Optional[Any] = None,
    vertical: Optional[str] = None,
    model_id: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> Agent:
    """Agente estruturado (saída `DetailedValidation`) com persistência.

    Args:
        db: Banco SQLite (agno) para persistência.
        vertical: Chave da vertical de mercado (ver `verticals.VERTICAIS`).
        model_id: Id do modelo DeepSeek (permite fallback explícito).
        max_tokens: Limite de tokens de saída.
    """
    instrucoes = list(prompts.AGENTE_ESTRUTURADO_INSTRUCOES)
    if vertical:
        v = get_vertical(vertical)
        instrucoes.extend(v.instrucoes)

    kwargs = _base_kwargs(db=db, model_id=model_id, max_tokens=max_tokens)
    return Agent(
        name="Analista de Startups",
        instructions=instrucoes,
        output_schema=DetailedValidation,
        stream=True,
        **kwargs,
    )


def build_free_text_agent(
    db: Optional[Any] = None,
    model_id: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> Agent:
    """Agente de texto livre (sem schema), para avaliações em texto corrido.

    Por padrão não recebe `db`, pois avaliações de texto (pitch, comparativo)
    não geram `DetailedValidation` e não devem poluir o histórico de validações.
    """
    kwargs = _base_kwargs(db=db, model_id=model_id, max_tokens=max_tokens)
    return Agent(
        name="Analista Comparador",
        instructions=list(prompts.AGENTE_TEXTO_LIVRE_INSTRUCOES),
        stream=False,
        **kwargs,
    )
