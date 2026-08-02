"""Serviço de histórico de validações."""

from datetime import datetime

from agno.agent import Agent

from startup_validator import db


def _format_timestamp(ts: int) -> str:
    try:
        return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")
    except (ValueError, OverflowError, OSError):
        return str(ts)


def get_history(agent: Agent) -> list:
    """Retorna a lista de validações com id, data e a ideia validada."""
    historico: list = []
    for session in db.list_sessions(agent.db):
        session_id = session.session_id
        data = _format_timestamp(session.created_at) if session.created_at else "-"
        ideia = _extract_idea(agent, session_id)
        historico.append({"id": session_id[:8], "data": data, "ideia": ideia})
    return historico


def _extract_idea(agent: Agent, session_id: str) -> str:
    try:
        messages = agent.get_session_messages(session_id=session_id)
        for msg in messages:
            if msg.role == "user" and isinstance(msg.content, str):
                return msg.content[:60]
    except Exception:
        pass
    return "—"
