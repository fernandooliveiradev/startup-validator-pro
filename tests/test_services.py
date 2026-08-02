"""Testes de serviços: cache, exportação e utilitários de parse."""

import json

from startup_validator import services
from startup_validator.schemas import DetailedValidation


def _modelo() -> DetailedValidation:
    return DetailedValidation(
        resumo="Assinatura de café artesanal.",
        pontos_fortes=["Nicho crescente"],
        pontos_fracos=["Logística cara"],
        analise_mercado="Mercado cresce ~15% ao ano.",
        score=70,
    )


def test_export_json():
    conteudo, ext = services.export_validation(_modelo(), "json")
    assert ext == "json"
    data = json.loads(conteudo)
    assert data["score"] == 70
    assert data["resumo"] == "Assinatura de café artesanal."


def test_export_markdown():
    conteudo, ext = services.export_validation(_modelo(), "md")
    assert ext == "md"
    assert "# Validação de Ideia" in conteudo


def test_from_any_aceita_objeto():
    assert DetailedValidation.from_any(_modelo()) is not None


def test_from_any_aceita_dict():
    m = DetailedValidation.from_any(_modelo().to_dict())
    assert m is not None and m.score == 70


def test_from_any_aceita_json():
    m = DetailedValidation.from_any(json.dumps(_modelo().to_dict()))
    assert m is not None and m.score == 70


def test_from_any_rejeita_lixo():
    assert DetailedValidation.from_any("não é json") is None


def test_normalize_remove_stopwords():
    alvo = services._normalize("aplicativo de assinatura de café")
    assert "aplicativo" in alvo
    assert "de" not in alvo
    assert "assinatura" in alvo
