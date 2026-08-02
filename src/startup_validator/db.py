"""Persistência das sessões de validação em SQLite."""

from typing import List

from agno.db.base import SessionType
from agno.db.sqlite import SqliteDb
from agno.session import AgentSession

from startup_validator import config
from startup_validator.config import ensure_dirs


def get_db() -> SqliteDb:
    """Retorna o banco SQLite usado para persistir as sessões do agente."""
    ensure_dirs()
    return SqliteDb(session_table=config.SESSION_TABLE, db_file=str(config.DB_FILE))


def list_sessions(db: SqliteDb) -> List[AgentSession]:
    """Lista as sessões de agente persistidas, da mais recente para a mais antiga."""
    sessions = db.get_sessions(
        session_type=SessionType.AGENT,
        sort_by="created_at",
        sort_order="desc",
    )
    return list(sessions or [])
