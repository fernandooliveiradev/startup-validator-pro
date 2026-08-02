"""Geração de artefatos em HTML (Tailwind CSS + Lucide icons) com tema claro/escuro.

Gera um arquivo `.html` autocontido (Tailwind e ícones via CDN) a partir de um
relatório estruturado (`DetailedValidation`) ou de conteúdo em Markdown, com
toggle de tema (claro/escuro), gauge de score, cards de indicadores e ícones
SVG (Lucide). O arquivo pode ser aberto direto no navegador.
"""

import html
from datetime import datetime
from pathlib import Path
from typing import Optional

from startup_validator import config
from startup_validator.schemas import DetailedValidation

_TAILWIND_CDN = "https://cdn.tailwindcss.com"
_LUCIDE_CDN = "https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"

# Cor do fundo escuro (quase preto).
_DARK_BG = "#0a0a0a"


def _escape(text: str) -> str:
    return html.escape(text or "")


# --- Renderização de Markdown simples ---


def _to_html_paragraphs(markdown: str) -> str:
    """Converte blocos simples de Markdown em HTML básico (títulos, listas, parágrafos)."""
    linhas = markdown.splitlines()
    blocos: list[str] = []
    i = 0
    while i < len(linhas):
        linha = linhas[i].rstrip()
        if not linha.strip():
            i += 1
            continue

        if linha.startswith("# "):
            blocos.append(f'<h1 class="text-2xl font-bold mt-6 text-neutral-900 dark:text-neutral-100">{_escape(linha[2:])}</h1>')
        elif linha.startswith("## "):
            blocos.append(f'<h2 class="text-xl font-semibold mt-5 text-neutral-900 dark:text-neutral-100">{_escape(linha[3:])}</h2>')
        elif linha.startswith("### "):
            blocos.append(f'<h3 class="text-lg font-semibold mt-4 text-neutral-900 dark:text-neutral-100">{_escape(linha[4:])}</h3>')
        elif linha.strip().startswith("- "):
            itens = []
            while i < len(linhas) and linhas[i].strip().startswith("- "):
                itens.append(linhas[i].strip()[2:])
                i += 1
            li = "\n".join(
                f'<li class="flex gap-2 text-neutral-700 dark:text-neutral-300"><i data-lucide="chevron-right" class="w-4 h-4 mt-1 text-neutral-400 shrink-0"></i><span>{_escape(item)}</span></li>'
                for item in itens
            )
            blocos.append(f'<ul class="mt-2 space-y-1.5">{li}</ul>')
            continue
        else:
            paragrafo = []
            while i < len(linhas) and linhas[i].strip() and not (
                linhas[i].lstrip().startswith(("#", "- "))
            ):
                paragrafo.append(linhas[i])
                i += 1
            texto = " ".join(p.strip() for p in paragrafo)
            blocos.append(
                f'<p class="mt-3 leading-relaxed text-neutral-700 dark:text-neutral-300">{_escape(texto)}</p>'
            )
        i += 1

    return "\n".join(blocos)


# --- Indicadores e componentes ---


def _score_gauge(score: Optional[int]) -> str:
    """Gauge circular SVG do score (0-100) com cor por faixa."""
    valor = score if score is not None else 0
    pct = max(0, min(100, valor)) / 100
    raio = 52
    circunferencia = 2 * 3.1416 * raio
    offset = circunferencia * (1 - pct)

    cor = "#22c55e" if valor >= 70 else ("#eab308" if valor >= 40 else "#ef4444")
    label = "Excelente" if valor >= 70 else ("Promissor" if valor >= 40 else "Risco alto")

    return f"""
<div class="flex flex-col items-center p-6 rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900">
  <div class="relative w-36 h-36">
    <svg viewBox="0 0 120 120" class="w-full h-full -rotate-90">
      <circle cx="60" cy="60" r="{raio}" fill="none" stroke="currentColor" stroke-width="10" class="text-neutral-200 dark:text-neutral-700"/>
      <circle cx="60" cy="60" r="{raio}" fill="none" stroke="{cor}" stroke-width="10" stroke-linecap="round"
        stroke-dasharray="{circunferencia}" stroke-dashoffset="{offset}" style="transition: stroke-dashoffset 1s ease"/>
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span class="text-4xl font-bold text-neutral-900 dark:text-neutral-100">{valor}</span>
      <span class="text-xs text-neutral-500">/ 100</span>
    </div>
  </div>
  <span class="mt-3 text-sm font-medium" style="color:{cor}">{label}</span>
</div>
"""


def _metric_card(icone: str, rotulo: str, valor: str, cor: str = "text-neutral-900 dark:text-neutral-100") -> str:
    """Card de indicador com ícone Lucide."""
    return f"""
<div class="flex items-start gap-3 p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900">
  <span class="w-9 h-9 rounded-lg flex items-center justify-center bg-neutral-100 dark:bg-neutral-800 shrink-0">
    <i data-lucide="{icone}" class="w-5 h-5 text-neutral-600 dark:text-neutral-300"></i>
  </span>
  <div>
    <div class="text-xs text-neutral-500 uppercase tracking-wide">{_escape(rotulo)}</div>
    <div class="text-sm font-medium {cor}">{_escape(valor)}</div>
  </div>
</div>
"""


def _list_section(icone: str, titulo: str, itens: list[str], acento: str) -> str:
    """Seção com título (ícone) e lista de itens, com cor de acento."""
    li = "\n".join(
        f'<li class="flex gap-2 text-neutral-700 dark:text-neutral-300">'
        f'<i data-lucide="{icone}" class="w-4 h-4 mt-1 shrink-0" style="color:{acento}"></i>'
        f'<span>{_escape(item)}</span></li>'
        for item in itens
    )
    return f"""
<div class="mt-6 rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-6">
  <h3 class="flex items-center gap-2 text-lg font-semibold text-neutral-900 dark:text-neutral-100">
    <i data-lucide="{icone}" class="w-5 h-5" style="color:{acento}"></i>{_escape(titulo)}
  </h3>
  <ul class="mt-3 space-y-2">{li}</ul>
</div>
"""


def _render_relatorio(modelo: DetailedValidation) -> str:
    """Renderiza o relatório estruturado como um dashboard profissional."""
    secao = []

    # Gauge + métricas
    secao.append('<div class="grid grid-cols-1 md:grid-cols-2 gap-4">')
    secao.append(_score_gauge(modelo.score))
    secao.append('<div class="grid grid-cols-1 gap-4 content-start">')
    if modelo.nivel_risco:
        secao.append(_metric_card("shield-alert", "Nível de risco", modelo.nivel_risco.capitalize()))
    if modelo.cac_estimado:
        secao.append(_metric_card("wallet", "CAC estimado", modelo.cac_estimado))
    if modelo.mvp_minimo:
        secao.append(_metric_card("rocket", "MVP mínimo", modelo.mvp_minimo))
    secao.append('</div></div>')

    # Resumo
    secao.append(
        f'<div class="mt-6 rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-6">'
        f'<h3 class="flex items-center gap-2 text-lg font-semibold"><i data-lucide="book-open" class="w-5 h-5 text-blue-500"></i>Resumo</h3>'
        f'<p class="mt-2 text-neutral-700 dark:text-neutral-300 leading-relaxed">{_escape(modelo.resumo)}</p></div>'
    )

    # Análise de mercado
    secao.append(
        f'<div class="mt-6 rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-6">'
        f'<h3 class="flex items-center gap-2 text-lg font-semibold"><i data-lucide="trending-up" class="w-5 h-5 text-emerald-500"></i>Análise de mercado</h3>'
        f'<p class="mt-2 text-neutral-700 dark:text-neutral-300 leading-relaxed">{_escape(modelo.analise_mercado)}</p></div>'
    )

    # Pontos fortes e fracos
    secao.append(
        _list_section("thumbs-up", "Pontos fortes", modelo.pontos_fortes or [], "#22c55e")
    )
    secao.append(
        _list_section("thumbs-down", "Pontos fracos", modelo.pontos_fracos or [], "#ef4444")
    )

    # Próximos passos
    if modelo.proximos_passos:
        secao.append(
            _list_section("list-checks", "Próximos passos (30 dias)", modelo.proximos_passos, "#3b82f6")
        )

    # Referências
    if modelo.referencias:
        li = "\n".join(
            f'<li class="flex gap-2 text-neutral-600 dark:text-neutral-400 text-sm">'
            f'<i data-lucide="link" class="w-4 h-4 mt-0.5 shrink-0 text-neutral-400"></i>'
            f'<span>{_escape(r)}</span></li>'
            for r in modelo.referencias
        )
        secao.append(
            f'<div class="mt-6 rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-6">'
            f'<h3 class="flex items-center gap-2 text-lg font-semibold"><i data-lucide="link-2" class="w-5 h-5 text-neutral-400"></i>Fontes (Tavily)</h3>'
            f'<ul class="mt-3 space-y-2">{li}</ul></div>'
        )

    return "\n".join(secao)


# --- Documento HTML ---


def _wrap(title: str, corpo_html: str) -> str:
    """Monta o documento HTML completo com Tailwind, Lucide e toggle de tema."""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_escape(title)}</title>
  <script src="{_TAILWIND_CDN}"></script>
  <script src="{_LUCIDE_CDN}"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class'
    }};
    (function() {{
      const saved = localStorage.getItem('theme');
      if (saved === 'dark' || (saved === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
        document.documentElement.classList.add('dark');
      }}
    }})();
    function toggleTheme() {{
      const root = document.documentElement;
      root.classList.toggle('dark');
      localStorage.setItem('theme', root.classList.contains('dark') ? 'dark' : 'light');
    }}
  </script>
</head>
<body class="bg-neutral-50 dark:bg-[#0a0a0a] text-neutral-900 dark:text-neutral-100 antialiased transition-colors">
  <header class="sticky top-0 z-10 border-b border-neutral-200 dark:border-neutral-800 bg-white/80 dark:bg-[#0a0a0a]/80 backdrop-blur">
    <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
      <div class="flex items-center gap-2 min-w-0">
        <i data-lucide="sparkles" class="w-5 h-5 text-indigo-500 shrink-0"></i>
        <h1 class="text-lg font-bold truncate">{_escape(title)}</h1>
      </div>
      <button onclick="toggleTheme()" class="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg border border-neutral-300 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors shrink-0">
        <i data-lucide="moon" class="w-4 h-4"></i>
        <span class="hidden sm:inline">Tema</span>
      </button>
    </div>
  </header>
  <main class="max-w-4xl mx-auto px-6 py-8">
    {corpo_html}
    <footer class="mt-12 pt-6 border-t border-neutral-200 dark:border-neutral-800 text-xs text-neutral-400 flex items-center gap-2">
      <i data-lucide="cpu" class="w-4 h-4"></i>
      <span>Gerado por {_escape(config.APP_NAME)} em {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
    </footer>
  </main>
  <script>
    if (window.lucide) {{ lucide.createIcons(); }}
  </script>
</body>
</html>
"""


def gerar_html_artefato(
    titulo: str,
    markdown: str,
    tipo: str = "relatorio",
    modelo: Optional[DetailedValidation] = None,
) -> str:
    """Gera o HTML completo para um artefato.

    Args:
        titulo: Título exibido no documento.
        markdown: Conteúdo em Markdown (fallback para tipos não estruturados).
        tipo: "relatorio", "pitch" ou "comparativo" (define o layout).
        modelo: `DetailedValidation` quando disponível (permite gráficos/cards).

    Returns:
        String com o documento HTML completo.
    """
    if tipo == "relatorio" and modelo is not None:
        corpo = _render_relatorio(modelo)
    elif tipo == "relatorio":
        corpo = _to_html_paragraphs(markdown)
    elif tipo == "pitch":
        corpo = f'<div class="rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-6">{_to_html_paragraphs(markdown)}</div>'
    else:  # comparativo
        corpo = _to_html_paragraphs(markdown)
    return _wrap(titulo, corpo)


def salvar_artefato(
    titulo: str,
    markdown: str,
    tipo: str,
    abrir: bool,
    modelo: Optional[DetailedValidation] = None,
) -> Path:
    """Gera, salva e (opcionalmente) abre o artefato HTML no navegador.

    Returns:
        Caminho do arquivo gerado.
    """
    config.ensure_dirs()
    nome = f"{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    caminho = config.ARTIFACTS_DIR / nome
    html_doc = gerar_html_artefato(titulo, markdown, tipo, modelo=modelo)
    caminho.write_text(html_doc, encoding="utf-8")

    if abrir:
        import webbrowser

        webbrowser.open(caminho.resolve().as_uri())
    return caminho
