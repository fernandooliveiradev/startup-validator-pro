"""Testes do modelo DetailedValidation."""

from startup_validator.schemas import DetailedValidation


def _modelo() -> DetailedValidation:
    return DetailedValidation(
        resumo="Assinatura de café artesanal.",
        pontos_fortes=["Nicho crescente", "Recorrência"],
        pontos_fracos=["Logística cara", "Churn alto"],
        analise_mercado="Mercado cresce ~15% ao ano.",
        score=72,
        nivel_risco="médio",
        cac_estimado="R$ 80",
        mvp_minimo="Landing + assinatura mensal",
        proximos_passos=["Validar com 10 clientes", "Testar logística"],
        referencias=["https://exemplo.com/mercado"],
    )


def test_to_panel_text_inclui_campos():
    texto = _modelo().to_panel_text()
    assert "RESUMO" in texto
    assert "PONTOS FORTES" in texto
    assert "PONTOS FRACOS" in texto
    assert "ANÁLISE DE MERCADO" in texto
    assert "72/100" in texto
    assert "médio" in texto
    assert "PRÓXIMOS PASSOS" in texto
    assert "FONTES" in texto


def test_to_markdown_inclui_campos():
    md = _modelo().to_markdown()
    assert "# Validação de Ideia" in md
    assert "## Pontos Fortes" in md
    assert "## Análise de Mercado" in md
    assert "72/100" in md
    assert "## MVP Mínimo" in md
    assert "## Fontes (Tavily)" in md


def test_to_dict_serializa_tudo():
    d = _modelo().to_dict()
    assert d["score"] == 72
    assert d["pontos_fortes"] == ["Nicho crescente", "Recorrência"]
    assert "referencias" in d


def test_score_valida_limites():
    import pydantic

    try:
        DetailedValidation(resumo="x", pontos_fortes=[], pontos_fracos=[], analise_mercado="x", score=101)
        assert False, "deveria falhar"
    except pydantic.ValidationError:
        pass
