"""Interface de terminal usando Rich."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from startup_validator import config

console = Console()


def print_banner() -> None:
    console.print(
        Panel.fit(
            f"🎓 [bold cyan]{config.APP_NAME} v{config.APP_VERSION}[/bold cyan]\n"
            f"[dim]{config.APP_TAGLINE}[/dim]",
            border_style="blue",
        )
    )


def print_menu() -> None:
    console.print("1. [bold green]Validar Nova Ideia[/bold green]")
    console.print("2. [bold yellow]Ver Histórico de Sessões[/bold yellow]")
    console.print("3. [bold magenta]Ver Relatório Completo de uma Validação[/bold magenta]")
    console.print("4. [bold red]Sair[/bold red]")


def ask_option() -> str:
    return Prompt.ask("\nEscolha uma opção", choices=["1", "2", "3", "4"])


def ask_idea() -> str:
    return Prompt.ask("\n[bold]Qual a sua ideia de startup?[/bold]")


def print_report(content: str) -> None:
    console.print(Panel(content, title="📊 RELATÓRIO", border_style="green"))


def print_no_history() -> None:
    console.print("[yellow]Nenhum histórico disponível.[/yellow]")


def print_history(historico: list) -> None:
    table = Table(title="Histórico de Validações")
    table.add_column("ID", style="dim")
    table.add_column("Data", style="cyan")
    table.add_column("Ideia", style="white")
    for item in historico:
        table.add_row(item["id_curto"], item["data"], item["ideia"])
    console.print(table)


def ask_session_id() -> str:
    return Prompt.ask("\n[bold]Digite o ID da validação (8 primeiros caracteres):[/bold]")


def print_report_not_found(session_id: str) -> None:
    console.print(f"[yellow]Nenhum relatório encontrado para o ID '{session_id}'.[/yellow]")


def print_error(message: str) -> None:
    console.print(f"[bold red]❌ {message}[/bold red]")
