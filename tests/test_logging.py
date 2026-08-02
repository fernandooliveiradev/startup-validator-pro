"""Testes da configuração de logging (silencia ruído de parsing do agno)."""

import logging

from startup_validator import logging_setup
from startup_validator.logging_setup import _filtro


def _captura(handler: logging.Handler, nivel: int, msg: str) -> list:
    """Registra emite um record e retorna se passou pelo handler."""
    record = logging.LogRecord("agno", nivel, "", 0, msg, None, None)
    return handler.handle(record)


def test_filtro_descarta_ruido_parsing():
    filtro = _filtro
    for msg in (
        "Failed to parse cleaned JSON: x",
        "All parsing attempts failed.",
        "Failed to convert response to output_schema",
    ):
        record = logging.LogRecord("agno", logging.WARNING, "", 0, msg, None, None)
        assert not filtro.filter(record), f"deveria descartar: {msg}"


def test_filtro_mantem_mensagens_normais():
    filtro = _filtro
    record = logging.LogRecord("agno", logging.ERROR, "", 0, "Erro real de conexão", None, None)
    assert filtro.filter(record)


def test_configurar_logging_aplica_filtro_no_agno():
    logging_setup.configurar_logging("INFO")
    raiz = logging.getLogger("agno")
    assert any(isinstance(f, type(_filtro)) for f in raiz.filters)


def test_configurar_logging_idempotente():
    logging_setup.configurar_logging()
    logging_setup.configurar_logging()
    raiz = logging.getLogger("agno")
    # filtro não é duplicado
    filtros = [f for f in raiz.filters if isinstance(f, type(_filtro))]
    assert len(filtros) == 1
