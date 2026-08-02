"""Handlers de cada comando do menu.

Cada função encapsula um fluxo completo, isolando a lógica de negócio do loop
de apresentação (`cli.py`). Isso centraliza regras e evita duplicação.
"""

import asyncio
from pathlib import Path

from agno.agent import Agent

from startup_validator import agent as agent_factory
from startup_validator import db, history, prompts, services, ui
from startup_validator.schemas import DetailedValidation
from startup_validator.stream import render_stream


def _prompt_for_session(agent: Agent, contexto: str):
    """Lista o histórico e pede um ID de validação. Retorna a sessão alvo."""
    historico = history.list_sessions(agent)
    if not historico:
        ui.print_no_history()
        return None
    ui.print_history(historico)
    id_curto = ui.ask_session_id()
    return next((s for s in historico if s["id_curto"] == id_curto), None)


async def cmd_validar(agent: Agent) -> None:
    """Valida uma nova ideia, com cache e streaming estruturado."""
    vertical = ui.ask_vertical()
    if vertical != "geral":
        agent = agent_factory.build_agent(db=agent.db, vertical=vertical)

    ideia = ui.ask_idea()
    if not ideia.strip():
        return

    cached = services.find_cached_validation(agent, ideia)
    if cached is not None and ui.ask_existing_report(ideia):
        ui.print_report(cached.to_panel_text())
        return

    ui.print_info(f"🚀 Analisando ideia: [bold]{ideia}[/bold]\n[dim]Pesquisando mercado e concorrentes...[/dim]")
    prompt = prompts.VALIDAR_IDEIA_TEMPLATE.format(ideia=ideia)
    stream = services.stream_validation(agent, prompt)
    modelo, texto = await render_stream(stream, ui.console, structured=True)

    if modelo is not None:
        ui.print_report(modelo.to_panel_text())
    elif texto.strip():
        ui.print_report(texto)
    else:
        ui.print_error("Não foi possível obter um relatório estruturado.")


async def cmd_refinar(agent: Agent) -> None:
    """Valida com refinamento iterativo."""
    vertical = ui.ask_vertical()
    if vertical != "geral":
        agent = agent_factory.build_agent(db=agent.db, vertical=vertical)

    ideia = ui.ask_idea()
    if not ideia.strip():
        return
    rodadas = ui.ask_refinement_rounds()

    ui.print_info(f"🔄 Refinando a ideia em {rodadas} rodada(s)...")
    final, modelo = await asyncio.to_thread(services.refine_idea, agent, ideia, rodadas)
    ui.print_report(modelo.to_panel_text())


async def cmd_pitch() -> None:
    """Pitch Deck Review: avalia a descrição como um investidor."""
    ideia = ui.ask_idea()
    if not ideia.strip():
        return

    ui.print_info("🎬 Revisando o pitch...")
    comparador = agent_factory.build_free_text_agent()
    prompt = prompts.PITCH_REVIEW_TEMPLATE.format(ideia=ideia)
    stream = services.stream_free_text(comparador, prompt)
    _, texto = await render_stream(stream, ui.console, structured=False)
    if texto.strip():
        ui.print_report(texto)


def cmd_historico(agent: Agent) -> None:
    """Exibe o histórico de validações."""
    historico = history.list_sessions(agent)
    if not historico:
        ui.print_no_history()
    else:
        ui.print_history(historico)


def cmd_relatorio(agent: Agent) -> None:
    """Exibe o relatório completo de uma validação."""
    alvo = _prompt_for_session(agent, "relatório")
    if alvo is None:
        return
    relatorio = history.get_full_report(agent, alvo["id"])
    if relatorio is None:
        ui.print_report_not_found(alvo["id_curto"])
    else:
        ui.print_report(relatorio)


async def cmd_comparar(agent: Agent) -> None:
    """Compara ideias do histórico e ranqueia a mais promissora."""
    historico = history.list_sessions(agent)
    if not historico:
        ui.print_no_history()
        return
    ui.print_history(historico)

    ids = ui.ask_session_ids_for_compare()
    modelos = []
    for id_curto in ids:
        alvo = next((s for s in historico if s["id_curto"] == id_curto), None)
        if alvo:
            m = history.get_full_report_model(agent, alvo["id"])
            if m:
                modelos.append(f"{alvo['ideia']}\nResumo: {m.resumo}")

    if len(modelos) < 2:
        ui.print_error("Compare pelo menos 2 validações válidas.")
        return

    comparador = agent_factory.build_free_text_agent()
    ui.print_info("⚖️ Gerando comparativo...")
    resultado = await asyncio.to_thread(services.compare_ideas, comparador, modelos)
    ui.print_report(resultado)


def cmd_exportar(agent: Agent) -> None:
    """Exporta uma validação em Markdown ou JSON."""
    alvo = _prompt_for_session(agent, "exportação")
    if alvo is None:
        return
    modelo = history.get_full_report_model(agent, alvo["id"])
    if modelo is None:
        ui.print_error("Nenhum modelo estruturado encontrado para exportar.")
        return

    formato = ui.ask_export_format()
    conteudo, ext = services.export_validation(modelo, formato)
    caminho = services.default_export_path(ext)
    Path(caminho).write_text(conteudo, encoding="utf-8")
    ui.print_info(f"✅ Exportado para [bold]{caminho}[/bold]")


async def cmd_ajuda() -> None:
    """Exibe a ajuda sobre o que o app faz."""
    ui.print_help()
