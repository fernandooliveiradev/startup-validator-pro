"""Testes da configuração de logging."""

import logging

from startup_validator import logging_setup


def test_httpx_logger_ajustado_para_warning():
    logging_setup.configurar_logging("INFO")
    assert logging.getLogger("httpx").level == logging.WARNING


def test_agno_logger_nao_e_silenciado():
    # Não deve existir filtro escondendo warnings de parsing do agno.
    logging_setup.configurar_logging("INFO")
    raiz = logging.getLogger("agno")
    assert raiz.filters == [], "nao deve silenciar o agno"


def test_configurar_logging_idempotente():
    logging_setup.configurar_logging()
    logging_setup.configurar_logging()
    # não lança erro em chamadas repetidas
    assert logging.getLogger("httpx").level == logging.WARNING
