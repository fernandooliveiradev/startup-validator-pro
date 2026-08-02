"""Ponto de entrada interativo do Startup Validator Pro."""

import asyncio
import sys

from startup_validator import agent as agent_factory
from startup_validator import config, db, history, ui


def _validate_env() -> None:
    """Valida as chaves de API necessárias e aborta com mensagem clara."""
    if not config.get_deepseek_api_key():
        ui.print_error("DEEPSEEK_API_KEY ausente. Copie .env.example para .env e preencha a chave.")
        sys.exit(1)
    if not config.get_tavily_api_key():
        ui.print_error("TAVILY_API_KEY ausente. Copie .env.example para .env e preencha a chave.")
        sys.exit(1)


async def main_app() -> None:
    _validate_env()

    database = db.get_db()
    analista = agent_factory.build_agent(db=database)

    while True:
        ui.print_banner()
        ui.print_menu()
        opcao = ui.ask_option()

        if opcao == "1":
            ideia = ui.ask_idea()
            if not ideia.strip():
                continue

            ui.print_report(f"🚀 Analisando ideia: [bold]{ideia}[/bold]\n[dim]Aguarde...[/dim]")
            try:
                run = await analista.arun(
                    f"Valide esta ideia de startup: {ideia}. Pesquise mercado e concorrentes."
                )
                ui.print_report(run.content.to_panel_text())
            except Exception as exc:  # noqa: BLE001 — UI deve exibir qualquer erro
                ui.print_error(f"Falha ao validar a ideia: {exc}")

        elif opcao == "2":
            historico = history.list_sessions(analista)
            if not historico:
                ui.print_no_history()
            else:
                ui.print_history(historico)

        elif opcao == "3":
            historico = history.list_sessions(analista)
            if not historico:
                ui.print_no_history()
                continue

            ui.print_history(historico)
            id_curto = ui.ask_session_id()
            alvo = next((s for s in historico if s["id_curto"] == id_curto), None)
            if alvo is None:
                ui.print_report_not_found(id_curto)
                continue

            relatorio = history.get_full_report(analista, alvo["id"])
            if relatorio is None:
                ui.print_report_not_found(id_curto)
            else:
                ui.print_report(relatorio)

        elif opcao == "4":
            break


def main() -> None:
    asyncio.run(main_app())


if __name__ == "__main__":
    main()
