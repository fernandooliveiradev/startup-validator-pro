"""Testes da fábrica de agentes."""

from unittest import mock

from agno.models.deepseek import DeepSeek

from startup_validator import agent as agent_factory


def _build_agent_mockado():
    """Constrói o agente com a tool mockada (sem chamar APIs)."""
    with mock.patch("startup_validator.agent.TavilyTools"):
        return agent_factory.build_agent()


def test_agente_estruturado_desliga_parse_response():
    """O agente estruturado usa parse_response=False para evitar o parsing
    heurístico de deltas parciais do agno (causa raiz do ruído), deixando o
    parse estruturado para a nossa camada de serviços."""
    a = _build_agent_mockado()
    assert a.parse_response is False


def test_agente_estruturado_tem_output_schema():
    from startup_validator.schemas import DetailedValidation

    a = _build_agent_mockado()
    assert a.output_schema is DetailedValidation


def test_agente_estruturado_usa_modelo_deepseek():
    a = _build_agent_mockado()
    assert isinstance(a.model, DeepSeek)
