"""Interface de terminal usando Rich."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from startup_validator import config, prompts

console = Console()

# Opções do menu agrupadas em seções.
_MENU_SECOES = [
    (
        "Criar",
        [
            ("1", "Validar Nova Ideia", "green"),
            ("2", "Validar com Refinamento Iterativo", "green"),
            ("3", "Pitch Deck Review", "green"),
        ],
    ),
    (
        "Gerenciar",
        [
            ("4", "Ver Histórico de Sessões", "yellow"),
            ("5", "Ver Relatório Completo de uma Validação", "magenta"),
            ("6", "Comparar Ideias do Histórico", "cyan"),
            ("7", "Exportar Validação (MD/JSON)", "blue"),
        ],
    ),
    (
        "Sistema",
        [
            ("0", "Ajuda", "dim"),
            ("8", "Sair", "red"),
        ],
    ),
]

# Mapeamento de escolhas disponíveis derivado das seções (evita hardcode).
_VALID_CHOICES = [op for _, opcoes in _MENU_SECOES for op, _, _ in opcoes]


def print_banner() -> None:
    console.print(
        Panel.fit(
            f"🎓 [bold cyan]{config.APP_NAME} v{config.APP_VERSION}[/bold cyan]\n"
            f"[dim]{config.APP_TAGLINE}[/dim]",
            border_style="blue",
        )
    )


def print_menu() -> None:
    for secao, opcoes in _MENU_SECOES:
        console.print(f"\n[bold underline]{secao}[/bold underline]")
        for opcao, label, cor in opcoes:
            console.print(f"{opcao}. [bold {cor}]{label}[/bold {cor}]")


def print_help() -> None:
    console.print(Panel(prompts.HELP_TEXT, title="ℹ️ Ajuda", border_style="cyan"))


def ask_option() -> str:
    return Prompt.ask("\nEscolha uma opção", choices=_VALID_CHOICES)


def ask_idea() -> str:
    return Prompt.ask("\n[bold]Qual a sua ideia de startup?[/bold]")


_VERTICAL_CHOICES = ["0", "1", "2", "3", "4", "5", "6"]
_VERTICAL_MAP = {
    "0": "geral",
    "1": "saas",
    "2": "ecommerce",
    "3": "foodtech",
    "4": "ai",
    "5": "marketplace",
    "6": "fintech",
}


def ask_vertical() -> str:
    console.print("\n[bold]Escolha a vertical (ou 0 para Geral):[/bold]")
    console.print(
        "[dim]1. SaaS B2B | 2. E-commerce | 3. Foodtech | 4. IA | 5. Marketplace | 6. Fintech | 0. Geral[/dim]"
    )
    escolha = Prompt.ask("Vertical", choices=_VERTICAL_CHOICES, default="0")
    return _VERTICAL_MAP[escolha]


def ask_refinement_rounds() -> int:
    try:
        return int(Prompt.ask("Quantas rodadas de refinamento?", default="2"))
    except ValueError:
        return 2


def ask_session_id() -> str:
    return Prompt.ask("\n[bold]Digite o ID da validação (8 primeiros caracteres):[/bold]")


def ask_session_ids_for_compare() -> list:
    resposta = Prompt.ask("\n[bold]IDs das validações (separados por vírgula):[/bold]")
    return [s.strip() for s in resposta.split(",") if s.strip()]


def ask_export_format() -> str:
    return Prompt.ask("Formato de exportação (md/json)?", choices=["md", "json"], default="md")


def ask_existing_report(ideia: str) -> bool:
    resp = Prompt.ask(
        "Este relatório já foi gerado para uma ideia similar. Abrir o existente? (s/n)",
        choices=["s", "n"],
        default="s",
    )
    return resp.lower() == "s"


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
