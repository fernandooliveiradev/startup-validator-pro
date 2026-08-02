"""Renderização em tempo real dos eventos de streaming no terminal."""

from typing import AsyncIterator, Optional, Tuple

from rich.console import Console
from rich.live import Live
from rich.text import Text

from startup_validator.services import to_validation_model
from startup_validator.schemas import DetailedValidation


async def render_stream(
    stream: AsyncIterator[dict],
    console: Console,
    structured: bool = True,
) -> Tuple[Optional[DetailedValidation], str]:
    """Consome eventos de streaming e renderiza ao vivo.

    Retorna `(modelo, texto_bruto)`:
    - `modelo`: o `DetailedValidation` final quando o modo é `structured` e o
      parse funciona; senão None.
    - `texto_bruto`: o texto completo acumulado, para uso como fallback ou
      como resultado no modo texto livre.

    Nunca trava: exibe raciocínio, chamadas de ferramenta e deltas em tempo
    real, e sempre consome todos os eventos até o `done`/`error`.
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
                else:
                    m = to_validation_model(c)
                    if m is not None:
                        final_model = m
                live.update(_render_state(buffer, thinking, status))
            elif tipo == "done":
                conteudo = item.get("conteudo")
                if structured and isinstance(conteudo, DetailedValidation):
                    final_model = conteudo
            elif tipo == "error":
                console.print(f"[bold red]❌ {item.get('erro', 'Erro desconhecido')}[/bold red]")
                return final_model, "".join(buffer)

    if thinking:
        console.print("\n[bold dim]🧠 Raciocínio:[/bold dim]")
        console.print("".join(thinking)[:1200])

    return final_model, "".join(buffer)


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
