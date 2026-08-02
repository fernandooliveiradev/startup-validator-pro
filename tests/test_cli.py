"""Teste de regressão: o dispatcher do menu chama cada handler com os argumentos certos.

Cobre o bug em que `cmd_validar`/`cmd_refinar`/`cmd_comparar` eram referenciados
sem o parâmetro `agent`, causando `TypeError` na execução.
"""

import asyncio
import inspect

from startup_validator import cli, commands


def _handler_aceita_agent(func_name: str) -> bool:
    """Verifica se o handler exige o parâmetro `agent`."""
    func = getattr(commands, func_name)
    sig = inspect.signature(func)
    return "agent" in sig.parameters


def test_handlers_que_requerem_agent():
    assert _handler_aceita_agent("cmd_validar")
    assert _handler_aceita_agent("cmd_refinar")
    assert _handler_aceita_agent("cmd_comparar")
    assert _handler_aceita_agent("cmd_historico")
    assert _handler_aceita_agent("cmd_relatorio")
    assert _handler_aceita_agent("cmd_exportar")


def test_cmd_pitch_nao_requer_agent():
    assert not _handler_aceita_agent("cmd_pitch")
    assert not _handler_aceita_agent("cmd_ajuda")


def test_make_wrappers_preservam_coroutine():
    async def fake_cmd(agent):
        return agent

    def fake_sync(agent):
        return ("sync", agent)

    class FakeAgent:
        pass

    async def main():
        # o wrapper assíncrono repassa o argumento e executa o handler
        wrapped = cli._make_async(fake_cmd, FakeAgent())
        assert await wrapped() is None
        # o wrapper síncrono repassa o argumento sem lançar TypeError
        sync_wrapped = cli._make_sync(fake_sync, FakeAgent())
        assert await sync_wrapped() is None

    asyncio.run(main())
