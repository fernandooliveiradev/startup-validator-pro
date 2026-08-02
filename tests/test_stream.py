"""Testes do streaming unificado."""

import asyncio

from startup_validator import services
from startup_validator.schemas import DetailedValidation


class FakeEvent:
    def __init__(self, event, content=None, rc=None, tool=None):
        self.event = event
        self.content = content
        self.reasoning_content = rc
        self.tool = tool


def _json_event():
    return FakeEvent(
        "RunContent",
        '{"resumo": "t", "pontos_fortes": ["a"], "pontos_fracos": ["b"], '
        '"analise_mercado": "m"}',
    )


class FakeAgent:
    def __init__(self, eventos=None):
        self.model = type("M", (), {"id": "deepseek-v4-flash"})()
        self._eventos = eventos or [_json_event(), FakeEvent("RunCompleted", "ok")]

    async def arun(self, ideia, stream=True):
        for e in self._eventos:
            yield e


def test_stream_validation_estruturado():
    async def main():
        tipos = []
        ag = FakeAgent([FakeEvent("RunContent", rc="pensando"), _json_event()])
        async for item in services.stream_validation(ag, "x"):
            tipos.append(item["tipo"])
            if item["tipo"] == "done":
                assert isinstance(item["conteudo"], DetailedValidation)
        assert "done" in tipos
        assert tipos.count("done") == 1
        assert "thinking" in tipos

    asyncio.run(main())


def test_stream_free_text_sempre_termina():
    async def main():
        tipos = []
        ag = FakeAgent([FakeEvent("RunContent", "ola"), FakeEvent("RunContent", " mundo")])
        async for item in services.stream_free_text(ag, "x"):
            tipos.append(item["tipo"])
            if item["tipo"] == "done":
                assert item["conteudo"] == "ola mundo"
        assert tipos.count("done") == 1

    asyncio.run(main())


def test_stream_emit_thinking():
    async def main():
        ag = FakeAgent([FakeEvent("RunContent", rc="pensando"), _json_event()])
        thinking = []
        async for item in services.stream_validation(ag, "x"):
            if item["tipo"] == "thinking":
                thinking.append(item["conteudo"])
        assert thinking == ["pensando"]

    asyncio.run(main())


def test_stream_parse_falha_no_delta_mas_recupera_no_fim():
    """Cobre a causa raiz: parsing falha em deltas parciais, mas o modelo é
    reconstruído a partir do conteúdo completo acumulado (fallback robusto)."""
    async def main():
        # Delta parcial que não é JSON válido sozinho, seguido do JSON completo.
        ag = FakeAgent(
            [
                FakeEvent("RunContent", '{"resumo": "par'),
                FakeEvent("RunContent", 'cial"}'),
                _json_event(),
            ]
        )
        modelo = None
        async for item in services.stream_validation(ag, "x"):
            if item["tipo"] == "done":
                modelo = item["conteudo"]
        assert isinstance(modelo, DetailedValidation)
        assert modelo.resumo == "t"

    asyncio.run(main())


def test_stream_sem_parser_entrega_texto_acumulado():
    async def main():
        ag = FakeAgent([FakeEvent("RunContent", "a"), FakeEvent("RunContent", "b")])
        texto = None
        async for item in services.stream_free_text(ag, "x"):
            if item["tipo"] == "done":
                texto = item["conteudo"]
        assert texto == "ab"

    asyncio.run(main())
