"""Configuração de logging do aplicativo.

Apenas ajusta o nível de log de bibliotecas de transporte (httpx/httpcore), que
emitem INFO a cada requisição HTTP — ruído irrelevante num CLI interativo.

Não silenciamos warnings de parsing do agno: o problema foi resolvido na causa
raiz (`parse_response=False` no agente estruturado), não escondido. Se houver
warnings de parsing, eles aparecem, pois sinalizam algo a investigar.
"""

import logging
from typing import Optional


def configurar_logging(nivel: Optional[str] = None) -> None:
    """Configura o logging do aplicativo.

    Args:
        nivel: Nível de log para a raiz (ex.: "INFO", "DEBUG"). Se None, usa INFO.
    """
    nivel = nivel or "INFO"
    logging.basicConfig(level=getattr(logging, nivel.upper(), logging.INFO))

    # Transporte HTTP (httpx/httpcore/hpack): INFO por requisição é ruído no CLI.
    for nome in ("httpx", "httpcore", "hpack"):
        logging.getLogger(nome).setLevel(logging.WARNING)
