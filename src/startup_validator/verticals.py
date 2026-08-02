"""Templates de análise especializada por vertical de mercado."""

from typing import Dict, Optional


class Vertical:
    """Configuração de instruções específicas para uma vertical."""

    def __init__(self, key: str, label: str, instrucoes: list) -> None:
        self.key = key
        self.label = label
        self.instrucoes = instrucoes


VERTICAIS: Dict[str, Vertical] = {
    "saas": Vertical(
        key="saas",
        label="SaaS B2B",
        instrucoes=[
            "Avalie métricas de SaaS: MRR/ARR, churn, CAC vs LTV, NRR.",
            "Considere concorrentes e posicionamento de produto no B2B.",
        ],
    ),
    "ecommerce": Vertical(
        key="ecommerce",
        label="E-commerce",
        instrucoes=[
            "Avalie margem, ticket médio, custo de frete, retenção e recorrência.",
            "Considere players de marketplace e canais de aquisição.",
        ],
    ),
    "foodtech": Vertical(
        key="foodtech",
        label="Foodtech",
        instrucoes=[
            "Avalie logística, shelf life, margem, regulatório e operação.",
            "Considere concorrentes de delivery e dark kitchen.",
        ],
    ),
    "ai": Vertical(
        key="ai",
        label="IA / AI-first",
        instrucoes=[
            "Avalie custo de inferência, moat real, dados proprietários e unidade econômica.",
            "Considere a velocidade de commoditização de recursos de IA.",
        ],
    ),
    "marketplace": Vertical(
        key="marketplace",
        label="Marketplace",
        instrucoes=[
            "Avalie efeito de rede, liquidez, problemas de dois lados e take rate.",
            "Considere o risco de chicken-and-egg e governança de oferta.",
        ],
    ),
    "fintech": Vertical(
        key="fintech",
        label="Fintech",
        instrucoes=[
            "Avalie regulatório (BACEN, LGPD), risco de crédito, custo de captação.",
            "Considere parcerias bancárias e barreiras de compliance.",
        ],
    ),
    "geral": Vertical(
        key="geral",
        label="Geral",
        instrucoes=[],
    ),
}


def get_vertical(key: Optional[str]) -> Vertical:
    return VERTICAIS.get(key or "", VERTICAIS["geral"])


def vertical_labels() -> list:
    return [(k, v.label) for k, v in VERTICAIS.items()]
