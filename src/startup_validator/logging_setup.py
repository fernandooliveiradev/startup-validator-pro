"""Configuração de logging do aplicativo.

Silencia warnings internos de parsing do agno que são ruído de streaming.
Durante o streaming, o agno tenta validar deltas parciais de JSON (que sempre
falham) e logga "Failed to parse..." a cada tentativa. Isso polui a tela sem
indicar erro real. Usamos um `logging.Filter` no logger `agno`, o que é imune
a qualquer reset de nível que o agno faça em runtime.
"""

import logging
from typing import Optional

# Padrões de mensagens internas do agno que são ruído (não indicam falha real).
_PADROES_RUIDO = (
    "Failed to parse cleaned JSON",
    "All parsing attempts failed",
    "Failed to convert response to output_schema",
    "Failed to convert response to output model",
)


class _FiltroRuidoAgno(logging.Filter):
    """Descarta mensagens de parsing ruidosas do agno."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not msg.startswith(_PADROES_RUIDO)


_filtro = _FiltroRuidoAgno()


def configurar_logging(nivel: Optional[str] = None) -> None:
    """Configura o logging do aplicativo.

    Args:
        nivel: Nível de log para a raiz (ex.: "INFO", "DEBUG"). Se None, usa INFO.
    """
    nivel = nivel or "INFO"
    logging.basicConfig(level=getattr(logging, nivel.upper(), logging.INFO))

    # Aplica o filtro ao logger do agno (e a toda a hierarquia agno.*), de forma
    # idempotente e imune a reset de nível.
    raiz = logging.getLogger("agno")
    if _filtro not in raiz.filters:
        raiz.addFilter(_filtro)

    # Silencia o ruído de transporte HTTP (httpx/httpcore), irrelevante no CLI.
    for nome in ("httpx", "httpcore", "hpack"):
        _logger = logging.getLogger(nome)
        _logger.setLevel(logging.WARNING)
