"""Serviço de histórico de validações."""

import json
from datetime import datetime

from agno.agent import Agent

from startup_validator import db
from startup_validator.schemas import DetailedValidation


def _format_timestamp(ts: int) -> str:
    try:
        return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")
    except (ValueError, OverflowError, OSError):
        return str(ts)


def list_sessions(agent: Agent) -> list:
    """Lista as sessões persistidas com id (completo e curto), data e a ideia validada."""
    resultado: list = []
    for session in db.list_sessions(agent.db):
        resultado.append(
            {
                "id": session.session_id,
                "id_curto": session.session_id[:8],
                "data": _format_timestamp(session.created_at) if session.created_at else "-",
                "ideia": _extract_idea(agent, session.session_id),
            }
        )
    return resultado


def get_full_report(agent: Agent, session_id: str) -> str | None:
    """Retorna o relatório completo de uma validação, ou None se não encontrado.

    Tenta reconstruir o modelo estruturado `DetailedValidation`; se não for
    possível, devolve o texto bruto da resposta do assistente.
    """
    try:
        messages = agent.get_session_messages(session_id=session_id)
    except Exception:
        return None

    for msg in messages:
        if msg.role != "assistant" or not isinstance(msg.content, str):
            continue
        content = msg.content.strip()
        if content.startswith("{") and '"resumo"' in content:
            return _render_report(content)
        if content:  # última resposta não-estruturada do assistente
            return content
    return None


def _render_report(raw_json: str) -> str:
    try:
        data = json.loads(raw_json)
        model = DetailedValidation.model_validate(data)
        return model.to_panel_text()
    except Exception:
        return raw_json


def _extract_idea(agent: Agent, session_id: str) -> str:
    try:
        messages = agent.get_session_messages(session_id=session_id)
        for msg in messages:
            if msg.role == "user" and isinstance(msg.content, str):
                return msg.content[:60]
    except Exception:
        pass
    return "—"
