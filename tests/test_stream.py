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
