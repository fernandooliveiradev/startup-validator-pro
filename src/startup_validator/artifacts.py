"""Geração de artefatos em HTML (Tailwind CSS) com tema claro/escuro.

Gera um arquivo `.html` autocontido (Tailwind via CDN) a partir de conteúdo
em Markdown, com toggle de tema (claro/escuro) e respeito ao
`prefers-color-scheme`. O arquivo pode ser aberto direto no navegador.
"""

import html
from datetime import datetime
from pathlib import Path

from startup_validator import config

_TAILWIND_CDN = "https://cdn.tailwindcss.com"


def _escape(text: str) -> str:
    return html.escape(text or "")


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

        # Títulos
        if linha.startswith("# "):
            blocos.append(f'<h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mt-6">{_escape(linha[2:])}</h1>')
        elif linha.startswith("## "):
            blocos.append(f'<h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mt-5">{_escape(linha[3:])}</h2>')
        elif linha.startswith("### "):
            blocos.append(f'<h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mt-4">{_escape(linha[4:])}</h3>')

        # Lista
        elif linha.strip().startswith("- "):
            itens = []
            while i < len(linhas) and linhas[i].strip().startswith("- "):
                itens.append(linhas[i].strip()[2:])
                i += 1
            li = "\n".join(
                f'<li class="text-neutral-700 dark:text-neutral-300">{_escape(item)}</li>' for item in itens
            )
            blocos.append(f'<ul class="list-disc list-inside mt-2 space-y-1">{li}</ul>')
            continue

        # Parágrafo / texto corrido
        else:
            paragrafo = []
            while i < len(linhas) and linhas[i].strip() and not (
                linhas[i].lstrip().startswith(("#", "- "))
            ):
                paragrafo.append(linhas[i])
                i += 1
            texto = " ".join(p.strip() for p in paragrafo)
            blocos.append(
                f'<p class="text-neutral-700 dark:text-neutral-300 mt-3 leading-relaxed">{_escape(texto)}</p>'
            )
        i += 1

    return "\n".join(blocos)


def _wrap(title: str, corpo_html: str) -> str:
    """Monta o documento HTML completo com Tailwind e toggle de tema."""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_escape(title)}</title>
  <script src="{_TAILWIND_CDN}"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class'
    }};
    // Tema inicial: respeita a preferência do sistema; permite alternância manual.
    (function() {{
      const saved = localStorage.getItem('theme');
      if (saved === 'dark' || (saved === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
        document.documentElement.classList.add('dark');
      }}
    }})();
    function toggleTheme() {{
      const root = document.documentElement;
      root.classList.toggle('dark');
      const isDark = root.classList.contains('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }}
  </script>
</head>
<body class="bg-white dark:bg-[#0a0a0a] text-neutral-900 dark:text-neutral-100 antialiased transition-colors">
  <header class="sticky top-0 z-10 border-b border-neutral-200 dark:border-neutral-800 bg-white/80 dark:bg-[#0a0a0a]/80 backdrop-blur">
    <div class="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
      <h1 class="text-lg font-bold truncate">{_escape(title)}</h1>
      <button onclick="toggleTheme()" class="px-3 py-1.5 text-sm rounded-lg border border-neutral-300 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors">
        🌗 Tema
      </button>
    </div>
  </header>
  <main class="max-w-3xl mx-auto px-6 py-8">
    {corpo_html}
    <footer class="mt-12 pt-6 border-t border-neutral-200 dark:border-neutral-800 text-xs text-neutral-400">
      Gerado por {_escape(config.APP_NAME)} em {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </footer>
  </main>
</body>
</html>
"""


def gerar_html_artefato(titulo: str, markdown: str, tipo: str = "relatorio") -> str:
    """Gera o HTML completo para um artefato a partir de conteúdo Markdown.

    Args:
        titulo: Título exibido no documento.
        markdown: Conteúdo em Markdown.
        tipo: "relatorio", "pitch" ou "comparativo" (define o layout).

    Returns:
        String com o documento HTML completo.
    """
    if tipo == "relatorio":
        corpo = _render_relatorio(markdown)
    elif tipo == "pitch":
        corpo = _to_html_paragraphs(markdown)
        corpo = f'<div class="bg-neutral-50 dark:bg-neutral-900 rounded-xl p-5">{corpo}</div>'
    else:  # comparativo
        corpo = _to_html_paragraphs(markdown)
    return _wrap(titulo, corpo)


def _render_relatorio(markdown: str) -> str:
    """Renderiza o relatório estruturado como blocos formatados."""
    return _to_html_paragraphs(markdown)


def salvar_artefato(titulo: str, markdown: str, tipo: str, abrir: bool) -> Path:
    """Gera, salva e (opcionalmente) abre o artefato HTML no navegador.

    Returns:
        Caminho do arquivo gerado.
    """
    config.ensure_dirs()
    nome = f"{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    caminho = config.ARTIFACTS_DIR / nome
    html_doc = gerar_html_artefato(titulo, markdown, tipo)
    caminho.write_text(html_doc, encoding="utf-8")

    if abrir:
        import webbrowser

        webbrowser.open(caminho.resolve().as_uri())
    return caminho
