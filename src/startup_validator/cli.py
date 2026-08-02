"""Ponto de entrada interativo do Startup Validator Pro."""

import asyncio
import sys

from startup_validator import commands, config, db, ui


def _validate_env() -> None:
    """Valida as chaves de API necessárias e aborta com mensagem clara."""
    if not config.get_deepseek_api_key():
        ui.print_error("DEEPSEEK_API_KEY ausente. Copie .env.example para .env e preencha a chave.")
        sys.exit(1)
    if not config.get_tavily_api_key():
        ui.print_error("TAVILY_API_KEY ausente. Copie .env.example para .env e preencha a chave.")
        sys.exit(1)


def _build_agent():
    from startup_validator import agent as agent_factory

    return agent_factory.build_agent(db=db.get_db(), vertical="geral")


async def main_app() -> None:
    _validate_env()
    analista = _build_agent()

    # Mapeia opção -> handler. Cada comando é isolado em `commands`.
    # Handlers podem ser síncronos ou assíncronos; `_run` normaliza ambos.
    handlers = {
        "0": commands.cmd_ajuda,
        "1": commands.cmd_validar,
        "2": commands.cmd_refinar,
        "3": commands.cmd_pitch,
        "4": _make_sync(commands.cmd_historico, analista),
        "5": _make_sync(commands.cmd_relatorio, analista),
        "6": _make_async(commands.cmd_comparar, analista),
        "7": _make_sync(commands.cmd_exportar, analista),
        "8": _sair,
    }

    while True:
        ui.print_banner()
        ui.print_menu()
        opcao = ui.ask_option()
        handler = handlers.get(opcao)
        if handler is None:
            ui.print_error("Opção inválida.")
            continue
        if opcao == "8":
            break
        try:
            await _run(handler)
        except (KeyboardInterrupt, EOFError):
            ui.print_info("\nOperação cancelada.")
        except Exception as exc:  # noqa: BLE001 — o CLI exibe qualquer erro
            ui.print_error(f"Erro: {exc}")


def _make_sync(func, arg):
    """Converte um handler síncrono em um callable sem argumentos."""

    async def _wrapped():
        func(arg)

    return _wrapped


def _make_async(func, arg):
    """Converte um handler assíncrono em um callable sem argumentos."""

    async def _wrapped():
        await func(arg)

    return _wrapped


async def _run(handler) -> None:
    """Executa um handler síncrono ou assíncrono."""
    resultado = handler()
    if asyncio.iscoroutine(resultado):
        await resultado


async def _sair() -> None:
    return None


def main() -> None:
    try:
        asyncio.run(main_app())
    except KeyboardInterrupt:
        ui.print_info("\nAté logo!")


if __name__ == "__main__":
    main()
