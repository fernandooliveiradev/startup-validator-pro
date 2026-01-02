import asyncio
import os
from pathlib import Path
from typing import List, Any

# IMPORTS OFICIAIS AGNO V2.3+
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
from agno.workflow import Workflow, WorkflowExecutionInput
from agno.db.base import SessionType
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

# --- 🛠️ Inicialização ---
load_dotenv()
console = Console()
Path("tmp").mkdir(exist_ok=True) 

if not os.getenv("OPENAI_API_KEY") or not os.getenv("TAVILY_API_KEY"):
    console.print("[bold red]❌ ERRO: Chaves de API ausentes no .env![/bold red]")
    exit(1)

# --- 1. Schema de Dados ---
class DetailedValidation(BaseModel):
    resumo: str = Field(..., description="Resumo da ideia.")
    pontos_fortes: List[str] = Field(..., description="Vantagens.")
    pontos_fracos: List[str] = Field(..., description="Riscos.")
    analise_mercado: str = Field(..., description="Análise de mercado 2025-2026.")

# --- 2. O Agente de Elite (Tavily) ---
analista_premium = Agent(
    name="Analista de Startups",
    model=OpenAIChat(id="gpt-4o"),
    tools=[TavilyTools()], 
    instructions=[
        "Você é um investidor-anjo sênior e brutalmente honesto.",
        "Sempre use o Tavily para buscar dados REAIS de mercado.",
    ],
    output_schema=DetailedValidation,
)

# --- 3. Lógica do Workflow ---
async def startup_validation_steps(
    workflow: Workflow,
    execution_input: WorkflowExecutionInput,
    startup_idea: str,
    **kwargs: Any,
) -> str:
    console.print(f"\n[bold green]🚀 Analisando Ideia:[/bold green] {startup_idea}")
    response = await analista_premium.arun(
        f"Valide esta ideia de startup: {startup_idea}. Pesquise mercado e concorrentes.",
        debug_mode=False 
    )
    data: DetailedValidation = response.content
    return f"""
[bold cyan]RESUMO:[/bold cyan] {data.resumo}

[bold green]PONTOS FORTES:[/bold green]
{chr(10).join(['- ' + p for p in data.pontos_fortes])}

[bold red]PONTOS FRACOS:[/bold red]
{chr(10).join(['- ' + p for p in data.pontos_fracos])}

[bold yellow]ANÁLISE DE MERCADO:[/bold yellow]
{data.analise_mercado}
"""

# --- 4. Definição do Workflow e Banco de Dados ---
startup_workflow = Workflow(
    name="Startup Validator Pro",
    db=SqliteDb(session_table="validations", db_file="tmp/workflows.db"), 
    steps=startup_validation_steps,
)

# --- 5. Menu Interativo ---
async def main_app():
    while True:
        console.print(Panel.fit(
            "🎓 [bold cyan]Startup Validator Pro v3.0[/bold cyan]\n[dim]Professor Python Elite Edition[/dim]",
            border_style="blue"
        ))
        
        console.print("1. [bold green]Validar Nova Ideia[/bold green]")
        console.print("2. [bold yellow]Ver Histórico de Sessões[/bold yellow]")
        console.print("3. [bold red]Sair[/bold red]")
        
        opcao = Prompt.ask("\nEscolha uma opção", choices=["1", "2", "3"])

        if opcao == "1":
            ideia = Prompt.ask("\n[bold]Qual a sua ideia de startup?[/bold]")
            if not ideia.strip(): continue
            
            result = await startup_workflow.arun(input="Nova Validação", startup_idea=ideia)
            console.print(Panel(result.content, title="📊 RELATÓRIO", border_style="green"))
            
        elif opcao == "2":
            # CORREÇÃO DEFINITIVA: Enum SessionType.WORKFLOW em MAIÚSCULAS
            sessions = startup_workflow.db.get_sessions(session_type=SessionType.WORKFLOW)
            
            if not sessions:
                console.print("[yellow]Nenhum histórico disponível.[/yellow]")
            else:
                table = Table(title="Histórico de Validações")
                table.add_column("ID", style="dim")
                table.add_column("Data", style="cyan")
                for s in sessions:
                    table.add_row(str(s.session_id)[:8], str(s.created_at))
                console.print(table)
                
        elif opcao == "3":
            break

if __name__ == "__main__":
    asyncio.run(main_app())