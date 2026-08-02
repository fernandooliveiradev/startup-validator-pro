"""Interface de terminal usando Rich."""

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

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
    console.print("2. [bold green]Validar com Refinamento Iterativo[/bold green]")
    console.print("3. [bold green]Pitch Deck Review[/bold green]")
    console.print("4. [bold yellow]Ver Histórico de Sessões[/bold yellow]")
    console.print("5. [bold magenta]Ver Relatório Completo de uma Validação[/bold magenta]")
    console.print("6. [bold cyan]Comparar Ideias do Histórico[/bold cyan]")
    console.print("7. [bold blue]Exportar Validação (MD/JSON)[/bold blue]")
    console.print("8. [bold red]Sair[/bold red]")


def ask_option() -> str:
    return Prompt.ask("\nEscolha uma opção", choices=[str(i) for i in range(1, 9)])


def ask_idea() -> str:
    return Prompt.ask("\n[bold]Qual a sua ideia de startup?[/bold]")


def ask_vertical() -> str:
    console.print("\n[bold]Escolha a vertical (ou Enter para Geral):[/bold]")
    console.print("[dim]1. SaaS B2B | 2. E-commerce | 3. Foodtech | 4. IA | 5. Marketplace | 6. Fintech | 0. Geral[/dim]")
    escolha = Prompt.ask("Vertical", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")
    mapa = {"0": "geral", "1": "saas", "2": "ecommerce", "3": "foodtech", "4": "ai", "5": "marketplace", "6": "fintech"}
    return mapa[escolha]


def ask_refinement_rounds() -> int:
    try:
        return int(Prompt.ask("Quantas rodadas de refinamento?", default="2"))
    except ValueError:
        return 2


def ask_session_id() -> str:
    return Prompt.ask("\n[bold]Digite o ID da validação (8 primeiros caracteres):[/bold]")


def ask_compare_count() -> int:
    try:
        return int(Prompt.ask("Quantas validações comparar?", default="2"))
    except ValueError:
        return 2


def ask_session_ids_for_compare() -> list:
    resposta = Prompt.ask("\n[bold]IDs das validações (separados por vírgula):[/bold]")
    return [s.strip() for s in resposta.split(",") if s.strip()]


def ask_export_format() -> str:
    return Prompt.ask("Formato de exportação (md/json)?", choices=["md", "json"], default="md")


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


def print_report_not_found(session_id: str) -> None:
    console.print(f"[yellow]Nenhum relatório encontrado para o ID '{session_id}'.[/yellow]")


def print_error(message: str) -> None:
    console.print(f"[bold red]❌ {message}[/bold red]")


def print_info(message: str) -> None:
    console.print(f"[dim]{message}[/dim]")


def print_idea_list(ideias: list) -> None:
    for i, ideia in enumerate(ideias, start=1):
        console.print(f"[cyan]{i}[/cyan]. {ideia}")


def ask_existing_report(ideia: str) -> bool:
    resp = Prompt.ask(
        "Este relatório já foi gerado para uma ideia similar. Abrir o existente? (s/n)",
        choices=["s", "n"],
        default="s",
    )
    return resp.lower() == "s"
