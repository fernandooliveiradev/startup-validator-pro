"""Modelos Pydantic usados para estruturar a resposta do agente."""

from typing import List, Optional

from pydantic import BaseModel, Field


class DetailedValidation(BaseModel):
    """Relatório estruturado de validação de uma ideia de startup."""

    resumo: str = Field(..., description="Resumo objetivo da ideia.")
    pontos_fortes: List[str] = Field(..., description="Vantagens e pontos fortes.")
    pontos_fracos: List[str] = Field(..., description="Riscos e pontos fracos.")
    analise_mercado: str = Field(
        ..., description="Análise de mercado 2025-2026 com dados reais pesquisados."
    )
    score: Optional[int] = Field(
        default=None, ge=0, le=100, description="Nota de viabilidade da ideia (0 a 100)."
    )
    nivel_risco: Optional[str] = Field(
        default=None, description="Nível de risco: baixo, médio ou alto."
    )
    cac_estimado: Optional[str] = Field(
        default=None, description="Estimativa de custo de aquisição de cliente (CAC)."
    )
    mvp_minimo: Optional[str] = Field(
        default=None, description="O que construir como MVP mínimo e como validar."
    )
    proximos_passos: Optional[List[str]] = Field(
        default=None, description="Ações acionáveis para os próximos 30 dias."
    )
    referencias: Optional[List[str]] = Field(
        default=None, description="Fontes/links pesquisados no Tavily (mercado e concorrentes)."
    )

    def to_panel_text(self) -> str:
        """Converte o relatório em texto formatado para exibição no terminal."""
        linhas = [f"[bold cyan]RESUMO:[/bold cyan] {self.resumo}", ""]
        linhas.append("[bold green]PONTOS FORTES:[/bold green]")
        linhas.extend(f"- {p}" for p in self.pontos_fortes)
        linhas.append("")
        linhas.append("[bold red]PONTOS FRACOS:[/bold red]")
        linhas.extend(f"- {p}" for p in self.pontos_fracos)
        linhas.append("")
        linhas.append("[bold yellow]ANÁLISE DE MERCADO:[/bold yellow]")
        linhas.append(self.analise_mercado)

        if self.score is not None:
            linhas.append("")
            linhas.append(f"[bold magenta]SCORE DE VIABILIDADE:[/bold magenta] {self.score}/100")
        if self.nivel_risco:
            cor = {"baixo": "green", "médio": "yellow", "alto": "red"}.get(
                self.nivel_risco.lower(), "white"
            )
            linhas.append(f"[bold]NÍVEL DE RISCO:[/bold] [{cor}]{self.nivel_risco}[/{cor}]")
        if self.cac_estimado:
            linhas.append(f"[bold]CAC ESTIMADO:[/bold] {self.cac_estimado}")
        if self.mvp_minimo:
            linhas.append("")
            linhas.append("[bold cyan]MVP MÍNIMO:[/bold cyan]")
            linhas.append(self.mvp_minimo)
        if self.proximos_passos:
            linhas.append("")
            linhas.append("[bold blue]PRÓXIMOS PASSOS (30 dias):[/bold blue]")
            linhas.extend(f"- {p}" for p in self.proximos_passos)
        if self.referencias:
            linhas.append("")
            linhas.append("[bold dim]FONTES (Tavily):[/bold dim]")
            linhas.extend(f"- {r}" for r in self.referencias)

        return "\n".join(linhas)

    def to_markdown(self) -> str:
        """Exporta o relatório em Markdown."""
        m = [f"# Validação de Ideia", "", f"**Resumo:** {self.resumo}", ""]
        m.append("## Pontos Fortes")
        m.extend(f"- {p}" for p in self.pontos_fortes)
        m.append("")
        m.append("## Pontos Fracos")
        m.extend(f"- {p}" for p in self.pontos_fracos)
        m.append("")
        m.append("## Análise de Mercado")
        m.append(self.analise_mercado)
        if self.score is not None:
            m += ["", f"**Score de viabilidade:** {self.score}/100"]
        if self.nivel_risco:
            m.append(f"**Nível de risco:** {self.nivel_risco}")
        if self.cac_estimado:
            m.append(f"**CAC estimado:** {self.cac_estimado}")
        if self.mvp_minimo:
            m += ["", "## MVP Mínimo", self.mvp_minimo]
        if self.proximos_passos:
            m += ["", "## Próximos Passos (30 dias)"]
            m.extend(f"- {p}" for p in self.proximos_passos)
        if self.referencias:
            m += ["", "## Fontes (Tavily)"]
            m.extend(f"- {r}" for r in self.referencias)
        return "\n".join(m)

    def to_dict(self) -> dict:
        """Exporta o relatório como dicionário serializável."""
        return self.model_dump()
