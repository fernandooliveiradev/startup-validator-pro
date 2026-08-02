"""Serviços de alto nível: cache, refinamento, comparativo e exportação."""

import json
import re
from datetime import datetime
from typing import Any, AsyncIterator, List, Optional, Tuple

from agno.agent import Agent

from startup_validator import config, db, history
from startup_validator.schemas import DetailedValidation

# Normalização mínima de palavras-chave para comparação fuzzy de ideias.
_STOPWORDS = {"de", "da", "do", "um", "uma", "para", "que", "com", "em", "o", "a", "os", "as", "e"}


def _normalize(text: str) -> set:
    palavras = re.findall(r"[a-zà-ú0-9]+", text.lower())
    return {p for p in palavras if p not in _STOPWORDS and len(p) > 2}


def find_cached_validation(agent: Agent, ideia: str) -> Optional[DetailedValidation]:
    """Retorna uma validação salva se uma ideia muito similar já foi validada."""
    alvo = _normalize(ideia)
    if not alvo:
        return None

    melhor = None
    melhor_overlap = 0.0
    for session in db.list_sessions(agent.db):
        relatorio = history.get_full_report_model(agent, session.session_id)
        if relatorio is None:
            continue
        # Compara a ideia de entrada apenas contra o resumo da validação salva.
        candidato = _normalize(relatorio.resumo or "")
        if not candidato:
            continue
        overlap = len(alvo & candidato) / len(alvo)
        if overlap >= 0.6 and overlap > melhor_overlap:
            melhor = relatorio
            melhor_overlap = overlap
    return melhor


def refine_idea(agent: Agent, ideia: str, iteracao: int = 2) -> Tuple[str, DetailedValidation]:
    """Refina a ideia em rodadas, incorporando feedback a cada validação.

    Retorna (ideia_final, ultima_validacao).
    """
    atual = ideia
    for rodada in range(iteracao):
        relatorio = _validate_once(agent, atual)
        pontos = relatorio.pontos_fracos
        feedback = "\n".join(f"- {p}" for p in (pontos or [])[:3])
        atual = (
            f"{atual}\n\n[Refinamento] Com base nos pontos fracos apontados abaixo, "
            f"apresente uma versão ajustada e melhor da ideia:\n{feedback}"
        )
    final = _validate_once(agent, atual)
    return atual, final


def _validate_once(agent: Agent, ideia: str) -> DetailedValidation:
    run = agent.run(f"Valide esta ideia de startup: {ideia}. Pesquise mercado e concorrentes.", stream=False)
    content = run.content
    if isinstance(content, DetailedValidation):
        return content
    raise ValueError("A resposta não pôde ser convertida em DetailedValidation.")


def compare_ideas(agent: Agent, ideias: List[str]) -> str:
    """Gera um relatório comparativo ranqueando as ideias."""
    prompt = (
        "Compare as seguintes ideias de startup e ranqueie da mais para a menos promissora, "
        "justificando cada posição com base em mercado, moat, dificuldade e unidade econômica:\n\n"
        + "\n".join(f"{i + 1}. {ideia}" for i, ideia in enumerate(ideias))
        + "\n\nResponda em português, em formato de lista ordenada com argumentos claros."
    )
    run = agent.run(prompt, stream=False)
    return str(run.content)


def export_validation(model: DetailedValidation, formato: str) -> Tuple[str, str]:
    """Serializa um relatório para exportação.

    Retorna (conteúdo, extensão_do_arquivo).
    """
    if formato == "json":
        return json.dumps(model.to_dict(), ensure_ascii=False, indent=2), "json"
    return model.to_markdown(), "md"


def default_export_path(formato: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"validation_{ts}.{formato}"


def _to_model(content) -> Optional[DetailedValidation]:
    if isinstance(content, DetailedValidation):
        return content
    if isinstance(content, str):
        try:
            data = json.loads(content)
            return DetailedValidation.model_validate(data)
        except Exception:
            return None
    if isinstance(content, dict):
        try:
            return DetailedValidation.model_validate(content)
        except Exception:
            return None
    return None


async def stream_validation(agent: Agent, ideia: str):
    """Executa a validação com streaming, emitindo eventos para a UI.

    Itera os eventos de `agent.arun(stream=True)` e emite deltas para o
    consumidor via um gerador assíncrono. Em caso de falha de modelo, tenta
    o modelo fallback (`FALLBACK_MODEL_ID`).

    Cada item emitido é um dict com uma das chaves:
        - tipo: "thinking", "tool_started", "tool_completed", "content", "done"
        - conteudo: o delta/texto/objeto relevante
        - erro: mensagem de erro (tipo "error")
    """
    yield {"tipo": "start"}
    try:
        async for evento in agent.arun(ideia, stream=True):
            nome = getattr(evento, "event", "")
            if nome in ("RunContent", "RunIntermediateContent", "RunCompleted"):
                c = getattr(evento, "content", None)
                yield {"tipo": "content", "conteudo": c}
                modelo = _to_model(c)
                if modelo is not None:
                    yield {"tipo": "done", "conteudo": modelo}
            elif nome == "ReasoningContentDelta":
                yield {"tipo": "thinking", "conteudo": getattr(evento, "reasoning_content", "")}
            elif nome == "ToolCallStarted":
                yield {"tipo": "tool_started", "conteudo": _tool_name(evento)}
            elif nome == "ToolCallCompleted":
                yield {"tipo": "tool_completed", "conteudo": _tool_name(evento)}
    except Exception as exc:
        # Fallback para o modelo pro.
        if agent.model.id != config.FALLBACK_MODEL_ID:
            agent.model = build_model_with_fallback()
            yield {"tipo": "info", "conteudo": f"Trocando para o modelo fallback ({config.FALLBACK_MODEL_ID})..."}
            async for evento in agent.arun(ideia, stream=True):
                nome = getattr(evento, "event", "")
                if nome in ("RunContent", "RunIntermediateContent", "RunCompleted"):
                    c = getattr(evento, "content", None)
                    yield {"tipo": "content", "conteudo": c}
                    modelo = _to_model(c)
                    if modelo is not None:
                        yield {"tipo": "done", "conteudo": modelo}
        else:
            yield {"tipo": "error", "erro": str(exc)}


def _tool_name(evento: Any) -> str:
    tool = getattr(evento, "tool", None)
    nome = getattr(tool, "tool_name", None) if tool else None
    return nome or "ferramenta"


def build_model_with_fallback():
    """Reutiliza a fábrica de modelo para instanciar o modelo fallback."""
    from startup_validator.agent import build_model

    return build_model(model_id=config.FALLBACK_MODEL_ID)
