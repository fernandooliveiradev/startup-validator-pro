"""Testes do módulo de prompts."""

from startup_validator import prompts


def test_prompts_tem_templates():
    assert hasattr(prompts, "VALIDAR_IDEIA_TEMPLATE")
    assert hasattr(prompts, "PITCH_REVIEW_TEMPLATE")
    assert hasattr(prompts, "REFINAR_FEEDBACK_TEMPLATE")
    assert hasattr(prompts, "COMPARAR_IDEAS_TEMPLATE")


def test_validar_template_format():
    texto = prompts.VALIDAR_IDEIA_TEMPLATE.format(ideia="café")
    assert "café" in texto
    assert "ideia" in texto


def test_pitch_template_format():
    texto = prompts.PITCH_REVIEW_TEMPLATE.format(relatorio="relatório de validação")
    assert "relatório de validação" in texto
    assert "investidor" in texto.lower()
    assert "PROPOSTA DE VALOR" in texto


def test_refinar_template_format():
    texto = prompts.REFINAR_FEEDBACK_TEMPLATE.format(ideia="x", feedback="- alto churn")
    assert "x" in texto
    assert "- alto churn" in texto


def test_comparar_template_format():
    texto = prompts.COMPARAR_IDEAS_TEMPLATE.format(ideias="1. a\n2. b")
    assert "1. a" in texto
    assert "ranqueie" in texto


def test_instrucoes_estruturadas_tem_persona():
    assert prompts.AGENTE_ESTRUTURADO_INSTRUCOES[0] == prompts.INVESTIDOR_PERSONA


def test_help_text_explica_opcoes():
    assert "Validar ideia" in prompts.HELP_TEXT
    assert "Pitch Deck Review" in prompts.HELP_TEXT
    assert "Exportar" in prompts.HELP_TEXT
