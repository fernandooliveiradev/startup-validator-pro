"""Ponto de entrada interativo do Startup Validator Pro."""

import asyncio
import sys
from pathlib import Path

from startup_validator import agent as agent_factory
from startup_validator import config, db, history, services, ui
from startup_validator.verticals import get_vertical


def _validate_env() -> None:
    """Valida as chaves de API necessárias e aborta com mensagem clara."""
    if not config.get_deepseek_api_key():
        ui.print_error("DEEPSEEK_API_KEY ausente. Copie .env.example para .env e preencha a chave.")
        sys.exit(1)
    if not config.get_tavily_api_key():
        ui.print_error("TAVILY_API_KEY ausente. Copie .env.example para .env e preencha a chave.")
        sys.exit(1)


def _build_agent(vertical: str):
    return agent_factory.build_agent(db=db.get_db(), vertical=vertical)


async def _run_validacao(analista, ideia: str) -> None:
    # Cache: não re-validar a mesma ideia.
    cached = services.find_cached_validation(analista, ideia)
    if cached is not None:
        if ui.ask_existing_report(ideia):
            ui.print_report(cached.to_panel_text())
            return

    ui.print_info(f"🚀 Analisando ideia: [bold]{ideia}[/bold]\n[dim]Pesquisando mercado e concorrentes...[/dim]")
    stream = services.stream_validation(analista, f"Valide esta ideia de startup: {ideia}. Pesquise mercado e concorrentes.")
    from startup_validator.stream import render_stream

    modelo, texto_bruto = await render_stream(stream, ui.console)
    if modelo is not None:
        ui.print_report(modelo.to_panel_text())
    elif texto_bruto.strip():
        ui.print_report(texto_bruto)
    else:
        ui.print_error("Não foi possível obter um relatório estruturado.")


async def main_app() -> None:
    _validate_env()

    analista = _build_agent(vertical="geral")

    while True:
        ui.print_banner()
        ui.print_menu()
        opcao = ui.ask_option()

        if opcao == "1":
            vertical = ui.ask_vertical()
            if vertical != "geral":
                analista = _build_agent(vertical=vertical)
            ideia = ui.ask_idea()
            if not ideia.strip():
                continue
            await _run_validacao(analista, ideia)

        elif opcao == "2":
            vertical = ui.ask_vertical()
            if vertical != "geral":
                analista = _build_agent(vertical=vertical)
            ideia = ui.ask_idea()
            if not ideia.strip():
                continue
            rodadas = ui.ask_refinement_rounds()
            ui.print_info(f"🔄 Refinando a ideia em {rodadas} rodada(s)...")
            final, modelo = await asyncio.to_thread(services.refine_idea, analista, ideia, rodadas)
            ui.print_report(modelo.to_panel_text())

        elif opcao == "3":
            ideia = ui.ask_idea()
            if not ideia.strip():
                continue
            ui.print_info("🎬 Revisando o pitch...")
            comparador = agent_factory.build_free_text_agent()
            stream = services.stream_free_text(
                comparador,
                f"O usuário descreveu a ideia de startup abaixo em texto. Revise como um "
                f"investidor-anjo avaliaria esse pitch: aponte forças, falhas, lacunas e o "
                f"que faltaria para investir.\n\nDescrição: {ideia}",
            )
            from startup_validator.stream import render_free_text

            texto = await render_free_text(stream, ui.console)
            if texto:
                ui.print_report(texto)

        elif opcao == "4":
            historico = history.list_sessions(analista)
            if not historico:
                ui.print_no_history()
            else:
                ui.print_history(historico)

        elif opcao == "5":
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

        elif opcao == "6":
            historico = history.list_sessions(analista)
            if not historico:
                ui.print_no_history()
                continue
            ui.print_history(historico)
            try:
                ids = ui.ask_session_ids_for_compare()
            except AttributeError:
                ui.print_error("Selecione os IDs separados por vírgula.")
                continue
            modelos = []
            for id_curto in ids:
                alvo = next((s for s in historico if s["id_curto"] == id_curto), None)
                if alvo:
                    m = history.get_full_report_model(analista, alvo["id"])
                    if m:
                        modelos.append(f"{alvo['ideia']}\nResumo: {m.resumo}")
            if len(modelos) < 2:
                ui.print_error("Compare pelo menos 2 validações válidas.")
                continue
            comparador = agent_factory.build_free_text_agent()
            ui.print_info("⚖️ Gerando comparativo...")
            resultado = await asyncio.to_thread(services.compare_ideas, comparador, modelos)
            ui.print_report(resultado)

        elif opcao == "7":
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
            modelo = history.get_full_report_model(analista, alvo["id"])
            if modelo is None:
                ui.print_error("Nenhum modelo estruturado encontrado para exportar.")
                continue
            formato = ui.ask_export_format()
            conteudo, ext = services.export_validation(modelo, formato)
            caminho = services.default_export_path(ext)
            Path(caminho).write_text(conteudo, encoding="utf-8")
            ui.print_info(f"✅ Exportado para [bold]{caminho}[/bold]")

        elif opcao == "8":
            break


def main() -> None:
    asyncio.run(main_app())


if __name__ == "__main__":
    main()
