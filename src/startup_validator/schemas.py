"""Modelos Pydantic usados para estruturar a resposta do agente."""

from typing import List

from pydantic import BaseModel, Field


class DetailedValidation(BaseModel):
    """Relatório estruturado de validação de uma ideia de startup."""

    resumo: str = Field(..., description="Resumo objetivo da ideia.")
    pontos_fortes: List[str] = Field(..., description="Vantagens e pontos fortes.")
    pontos_fracos: List[str] = Field(..., description="Riscos e pontos fracos.")
    analise_mercado: str = Field(
        ..., description="Análise de mercado 2025-2026 com dados reais pesquisados."
    )

    def to_panel_text(self) -> str:
        """Converte o relatório em texto formatado para exibição no terminal."""
        linhas = [f"[bold cyan]RESUMO:[/bold cyan] {self.resumo}"]
        linhas.append("")
        linhas.append("[bold green]PONTOS FORTES:[/bold green]")
        linhas.extend(f"- {p}" for p in self.pontos_fortes)
        linhas.append("")
        linhas.append("[bold red]PONTOS FRACOS:[/bold red]")
        linhas.extend(f"- {p}" for p in self.pontos_fracos)
        linhas.append("")
        linhas.append("[bold yellow]ANÁLISE DE MERCADO:[/bold yellow]")
        linhas.append(self.analise_mercado)
        return "\n".join(linhas)
