"""Testes do módulo de verticais."""

from startup_validator.verticals import get_vertical, vertical_labels


def test_get_vertical_geral_default():
    v = get_vertical(None)
    assert v.key == "geral"
    assert v.instrucoes == []


def test_get_vertical_especifica():
    v = get_vertical("saas")
    assert v.key == "saas"
    assert any("MRR" in instr for instr in v.instrucoes)


def test_vertical_desconhecida_cai_em_geral():
    v = get_vertical("nada_que_existe")
    assert v.key == "geral"


def test_vertical_labels():
    labels = vertical_labels()
    chaves = [k for k, _ in labels]
    assert "saas" in chaves
    assert "geral" in chaves
