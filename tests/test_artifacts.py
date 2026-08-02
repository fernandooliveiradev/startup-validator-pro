"""Testes do módulo de artefatos HTML."""

from startup_validator import artifacts
from startup_validator.schemas import DetailedValidation


def _modelo() -> DetailedValidation:
    return DetailedValidation(
        resumo="Assinatura de café artesanal.",
        pontos_fortes=["Nicho crescente", "Recorrência"],
        pontos_fracos=["Logística cara"],
        analise_mercado="Mercado cresce ~15% ao ano.",
        score=72,
        nivel_risco="médio",
        cac_estimado="R$ 80",
        mvp_minimo="Landing + assinatura",
        proximos_passos=["Validar com 10 clientes"],
        referencias=["https://exemplo.com"],
    )


def test_html_tem_tailwind_e_toggle():
    html_doc = artifacts.gerar_html_artefato("Título", _modelo().to_markdown(), "relatorio")
    assert "tailwindcss.com" in html_doc
    assert "toggleTheme" in html_doc
    assert "dark:" in html_doc
    assert "localStorage" in html_doc


def test_html_relatorio_inclui_conteudo():
    html_doc = artifacts.gerar_html_artefato("Título", _modelo().to_markdown(), "relatorio")
    assert "Assinatura de café artesanal" in html_doc
    assert "<h1" in html_doc


def test_html_markdown_listas_viram_ul_li():
    md = "## Titulo\n- item1\n- item2\nparagrafo."
    for tipo in ("pitch", "comparativo"):
        html_doc = artifacts.gerar_html_artefato("T", md, tipo)
        assert "<ul" in html_doc
        assert "item1" in html_doc
        assert "toggleTheme" in html_doc


def test_escape_evita_injecao():
    md = "texto <script>alert('x')</script>"
    html_doc = artifacts.gerar_html_artefato("T", md, "relatorio")
    assert "<script>alert" not in html_doc
    assert "&lt;script&gt;" in html_doc


def test_dashboard_relatorio_com_modelo_tem_gauge_e_cards():
    html_doc = artifacts.gerar_html_artefato(
        "T", _modelo().to_markdown(), "relatorio", modelo=_modelo()
    )
    # Gauge de score
    assert "stroke-dasharray" in html_doc
    assert ">72<" in html_doc
    # Ícones Lucide (não emojis)
    assert "lucide" in html_doc
    assert "shield-alert" in html_doc
    assert "wallet" in html_doc
    # Cards de métricas
    assert "CAC estimado" in html_doc
    assert "Nível de risco" in html_doc
    # Seções
    assert "Pontos fortes" in html_doc
    assert "Pontos fracos" in html_doc
    assert "Próximos passos" in html_doc


def test_dashboard_escape_conteudo_do_modelo():
    modelo = _modelo()
    modelo.resumo = "<script>alert(1)</script>"
    html_doc = artifacts.gerar_html_artefato("T", "", "relatorio", modelo=modelo)
    assert "<script>alert" not in html_doc
    assert "&lt;script&gt;" in html_doc
