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
    """Retorna o relatório completo (texto) de uma validação, ou None."""
    model = get_full_report_model(agent, session_id)
    if model is not None:
        return model.to_panel_text()

    # Fallback: texto bruto da última resposta do assistente.
    try:
        messages = agent.get_session_messages(session_id=session_id)
    except Exception:
        return None
    for msg in messages:
        if msg.role == "assistant" and isinstance(msg.content, str) and msg.content.strip():
            return msg.content
    return None


def get_full_report_model(agent: Agent, session_id: str) -> DetailedValidation | None:
    """Retorna o modelo `DetailedValidation` de uma validação salva, ou None."""
    try:
        messages = agent.get_session_messages(session_id=session_id)
    except Exception:
        return None

    for msg in messages:
        if msg.role != "assistant" or not isinstance(msg.content, str):
            continue
        content = msg.content.strip()
        if content.startswith("{") and '"resumo"' in content:
            try:
                data = json.loads(content)
                return DetailedValidation.model_validate(data)
            except Exception:
                continue
    return None


def _extract_idea(agent: Agent, session_id: str) -> str:
    try:
        messages = agent.get_session_messages(session_id=session_id)
        for msg in messages:
            if msg.role == "user" and isinstance(msg.content, str):
                return msg.content[:60]
    except Exception:
        pass
    return "—"
