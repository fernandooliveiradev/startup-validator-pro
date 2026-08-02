"""Serviços de alto nível: cache, refinamento, comparativo, exportação e streaming."""

import json
import re
from datetime import datetime
from typing import Any, AsyncIterator, Callable, List, Optional, Tuple

from agno.agent import Agent

from startup_validator import config, db, history, prompts
from startup_validator.schemas import DetailedValidation

# Normalização mínima de palavras-chave para comparação fuzzy de ideias.
_STOPWORDS = {"de", "da", "do", "um", "uma", "para", "que", "com", "em", "o", "a", "os", "as", "e"}
_CACHE_THRESHOLD = 0.6


def _normalize(text: str) -> set:
    palavras = re.findall(r"[a-zà-ú0-9]+", text.lower())
    return {p for p in palavras if p not in _STOPWORDS and len(p) > 2}


# --- Cache de validação ---

def find_cached_validation(agent: Agent, ideia: str) -> Optional[DetailedValidation]:
    """Retorna uma validação salva se uma ideia muito similar já foi validada."""
    alvo = _normalize(ideia)
    if not alvo:
        return None

    melhor: Optional[DetailedValidation] = None
    melhor_overlap = 0.0
    for session in db.list_sessions(agent.db):
        relatorio = history.get_full_report_model(agent, session.session_id)
        if relatorio is None:
            continue
        candidato = _normalize(relatorio.resumo or "")
        if not candidato:
            continue
        overlap = len(alvo & candidato) / len(alvo)
        if overlap >= _CACHE_THRESHOLD and overlap > melhor_overlap:
            melhor = relatorio
            melhor_overlap = overlap
    return melhor


# --- Refinamento e comparativo ---

def refine_idea(agent: Agent, ideia: str, iteracao: int = 2) -> Tuple[str, DetailedValidation]:
    """Refina a ideia em rodadas, incorporando feedback a cada validação.

    Retorna (ideia_final, ultima_validacao).
    """
    atual = ideia
    for _ in range(iteracao):
        relatorio = _validate_once(agent, atual)
        pontos = relatorio.pontos_fracos
        feedback = "\n".join(f"- {p}" for p in (pontos or [])[:3])
        atual = prompts.REFINAR_FEEDBACK_TEMPLATE.format(ideia=atual, feedback=feedback)
    final = _validate_once(agent, atual)
    return atual, final


def _validate_once(agent: Agent, ideia: str) -> DetailedValidation:
    """Valida a ideia e devolve o modelo `DetailedValidation`.

    O agno nem sempre converte a resposta para o objeto estruturado (parsing
    falha intermitentemente no DeepSeek). Por isso, tenta primeiro o objeto
    direto e, se necessário, faz o parse do conteúdo bruto ou das mensagens
    da sessão.
    """
    prompt = prompts.VALIDAR_IDEIA_TEMPLATE.format(ideia=ideia)
    run = agent.run(prompt, stream=False)
    modelo = DetailedValidation.from_any(run.content)
    if modelo is not None:
        return modelo

    if run.session_id:
        modelo = history.get_full_report_model(agent, run.session_id)
        if modelo is not None:
            return modelo

    raise ValueError("A resposta não pôde ser convertida em DetailedValidation.")


def compare_ideas(agent: Agent, ideias: List[str]) -> str:
    """Gera um relatório comparativo ranqueando as ideias."""
    lista = "\n".join(f"{i + 1}. {ideia}" for i, ideia in enumerate(ideias))
    prompt = prompts.COMPARAR_IDEAS_TEMPLATE.format(ideias=lista)
    run = agent.run(prompt, stream=False)
    return str(run.content)


# --- Exportação ---

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


# --- Streaming ---

EventParser = Callable[[Any], Optional[DetailedValidation]]


def _tool_name(evento: Any) -> str:
    tool = getattr(evento, "tool", None)
    nome = getattr(tool, "tool_name", None) if tool else None
    return nome or "ferramenta"


async def stream_run(agent: Agent, ideia: str, parser: Optional[EventParser] = None):
    """Executa a chamada de IA com streaming, emitindo eventos para a UI.

    Unifica o streaming estruturado e o de texto livre:
    - `parser` é uma função que tenta converter cada conteúdo em `DetailedValidation`.
      Se for None, o modo é texto livre (sempre termina com o texto final).

    Em caso de falha de modelo, tenta o fallback (`FALLBACK_MODEL_ID`).

    Eventos emitidos (dict):
        tipo: "start" | "thinking" | "tool_started" | "tool_completed"
              | "content" | "done" | "error" | "info"
    """
    yield {"tipo": "start"}
    deltas: list = []
    modelo_final: Optional[DetailedValidation] = None

    async def _coletar():
        nonlocal modelo_final
        async for evento in agent.arun(ideia, stream=True):
            nome = getattr(evento, "event", "")
            if nome in ("RunContent", "RunIntermediateContent", "RunCompleted"):
                # O raciocínio do DeepSeek chega dentro do RunContent, não em
                # evento separado. Emitimos como "thinking" em tempo real.
                rc = getattr(evento, "reasoning_content", None)
                if rc:
                    yield {"tipo": "thinking", "conteudo": rc}
                c = getattr(evento, "content", None)
                if isinstance(c, str) and c.strip():
                    deltas.append(c)
                    yield {"tipo": "content", "conteudo": c}
                if parser is not None:
                    m = parser(c)
                    if m is not None:
                        modelo_final = m
            elif nome == "ReasoningContentDelta":
                yield {"tipo": "thinking", "conteudo": getattr(evento, "reasoning_content", "")}
            elif nome == "ToolCallStarted":
                yield {"tipo": "tool_started", "conteudo": _tool_name(evento)}
            elif nome == "ToolCallCompleted":
                yield {"tipo": "tool_completed", "conteudo": _tool_name(evento)}

    try:
        async for item in _coletar():
            yield item
    except Exception as exc:
        if agent.model.id != config.FALLBACK_MODEL_ID:
            agent.model = build_model_with_fallback()
            yield {"tipo": "info", "conteudo": f"Trocando para o modelo fallback ({config.FALLBACK_MODEL_ID})..."}
            async for item in _coletar():
                yield item
        else:
            yield {"tipo": "error", "erro": str(exc)}
            return

    # Parse do conteúdo completo acumulado, se ainda não tiver modelo.
    if modelo_final is None and deltas:
        modelo_final = DetailedValidation.from_any("".join(deltas)) or DetailedValidation.from_any(deltas[-1])

    if parser is not None:
        yield {"tipo": "done", "conteudo": modelo_final}
    else:
        texto = "".join(deltas) or "Sem resposta."
        yield {"tipo": "done", "conteudo": texto}


def stream_validation(agent: Agent, ideia: str):
    """Streaming de validação estruturada (parser de `DetailedValidation`)."""
    return stream_run(agent, ideia, parser=DetailedValidation.from_any)


def stream_free_text(agent: Agent, ideia: str):
    """Streaming de texto livre (sem parser estruturado)."""
    return stream_run(agent, ideia, parser=None)


def build_model_with_fallback():
    """Reutiliza a fábrica de modelo para instanciar o modelo fallback."""
    from startup_validator.agent import build_model

    return build_model(model_id=config.FALLBACK_MODEL_ID)
