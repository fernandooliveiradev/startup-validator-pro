"""Renderização em tempo real dos eventos de streaming no terminal."""

from typing import AsyncIterator, Optional, Tuple

from rich.console import Console
from rich.live import Live
from rich.text import Text

from startup_validator.schemas import DetailedValidation

# Estados visuais durante o streaming.
_TOOL_SPINNER = "dots"
_TOOL_COLOR = "cyan"


async def render_stream(stream: AsyncIterator[dict], console: Console) -> Tuple[Optional[DetailedValidation], str]:
    """Consome o gerador de eventos de streaming e renderiza ao vivo.

    Retorna uma tupla `(modelo, texto_bruto)`: o `DetailedValidation` final
    quando disponível (senão None) e o texto completo acumulado, para uso
    como fallback quando o parsing estruturado falha.
    """
    final_model: Optional[DetailedValidation] = None
    buffer: list = []
    thinking: list = []
    status: list = []

    with Live(console=console, refresh_per_second=12, transient=False) as live:
        async for item in stream:
            tipo = item.get("tipo")

            if tipo == "start":
                live.update(Text("🚀 Iniciando análise...", style="bold cyan"))
            elif tipo == "thinking":
                delta = item.get("conteudo", "")
                if delta:
                    thinking.append(delta)
                    live.update(_render_state(buffer, thinking, status))
            elif tipo in ("tool_started", "tool_completed"):
                nome = item.get("conteudo", "ferramenta")
                if tipo == "tool_started":
                    status.append(f"🔍 Pesquisando via {nome}...")
                else:
                    status.append(f"✅ Pesquisa via {nome} concluída")
                live.update(_render_state(buffer, thinking, status))
            elif tipo == "info":
                status.append(str(item.get("conteudo", "")))
                live.update(_render_state(buffer, thinking, status))
            elif tipo == "content":
                c = item.get("conteudo")
                if isinstance(c, str) and c.strip():
                    buffer.append(c)
                elif isinstance(c, DetailedValidation):
                    final_model = c
                elif isinstance(c, dict):
                    try:
                        final_model = DetailedValidation.model_validate(c)
                    except Exception:
                        pass
                live.update(_render_state(buffer, thinking, status))
            elif tipo == "done":
                if item.get("conteudo") and isinstance(item["conteudo"], DetailedValidation):
                    final_model = item["conteudo"]
            elif tipo == "error":
                console.print(f"[bold red]❌ {item.get('erro', 'Erro desconhecido')}[/bold red]")
                return None, "".join(buffer)

    # Mostra o raciocínio completo, se houver.
    if thinking:
        console.print("\n[bold dim]🧠 Raciocínio:[/bold dim]")
        console.print("".join(thinking)[:1200])

    return final_model, "".join(buffer)


async def render_free_text(stream: AsyncIterator[dict], console: Console) -> str:
    """Consome eventos de streaming de texto livre e retorna o texto final.

    Nunca trava: exibe os deltas ao vivo e devolve o conteúdo final completo,
    mesmo que a resposta não seja estruturada.
    """
    buffer: list = []
    thinking: list = []
    status: list = []
    final_content = ""

    with Live(console=console, refresh_per_second=12, transient=False) as live:
        async for item in stream:
            tipo = item.get("tipo")

            if tipo == "start":
                live.update(Text("🚀 Iniciando análise...", style="bold cyan"))
            elif tipo == "thinking":
                delta = item.get("conteudo", "")
                if delta:
                    thinking.append(delta)
                    live.update(_render_state(buffer, thinking, status))
            elif tipo in ("tool_started", "tool_completed"):
                nome = item.get("conteudo", "ferramenta")
                if tipo == "tool_started":
                    status.append(f"🔍 Pesquisando via {nome}...")
                else:
                    status.append(f"✅ Pesquisa via {nome} concluída")
                live.update(_render_state(buffer, thinking, status))
            elif tipo == "info":
                status.append(str(item.get("conteudo", "")))
                live.update(_render_state(buffer, thinking, status))
            elif tipo == "content":
                c = item.get("conteudo")
                if isinstance(c, str) and c.strip():
                    buffer.append(c)
                live.update(_render_state(buffer, thinking, status))
            elif tipo == "done":
                final_content = str(item.get("conteudo", ""))
            elif tipo == "error":
                console.print(f"[bold red]❌ {item.get('erro', 'Erro desconhecido')}[/bold red]")
                return ""

    if thinking:
        console.print("\n[bold dim]🧠 Raciocínio:[/bold dim]")
        console.print("".join(thinking)[:1200])

    return final_content if final_content else "".join(buffer)


def _render_state(buffer: list, thinking: list, status: list) -> Text:
    t = Text()
    if status:
        t.append("\n".join(status), style="dim")
        t.append("\n\n")
    if buffer:
        t.append("".join(buffer), style="")
    elif thinking:
        trecho = "".join(thinking)[-400:]
        t.append("🧠 Pensando: ", style="bold yellow")
        t.append(trecho, style="yellow")
    return t
