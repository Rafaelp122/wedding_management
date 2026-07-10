"""
Templates de Cronograma para Casamentos.

Cada template é uma lista de eventos pré-definidos com offset em dias
antes da data do casamento. Usado na criação de um Wedding para
popular automaticamente o calendário.

Referência: UC08, Sprint 4
"""

from typing import Any

from apps.core.exceptions import BusinessRuleViolation


# ── Template: Religioso 12 meses ────────────────────────────────────────

RELIGIOUS_12M_TEMPLATE: list[dict[str, Any]] = [
    {
        "title": "Definir local da cerimônia",
        "event_type": "reuniao",
        "offset_days": 365,
    },
    {
        "title": "Contratar celebrante",
        "event_type": "reuniao",
        "offset_days": 330,
    },
    {
        "title": "Prova do vestido de noiva",
        "event_type": "visita",
        "offset_days": 300,
    },
    {
        "title": "Reunião com cerimonial",
        "event_type": "reuniao",
        "offset_days": 270,
    },
    {
        "title": "Contratar músicos/banda",
        "event_type": "reuniao",
        "offset_days": 240,
    },
    {
        "title": "Degustação do buffet",
        "event_type": "degustacao",
        "offset_days": 180,
    },
    {
        "title": "Escolher convite",
        "event_type": "outro",
        "offset_days": 150,
    },
    {
        "title": "Prova de cabelo e maquiagem",
        "event_type": "visita",
        "offset_days": 90,
    },
    {
        "title": "Ensaio geral da cerimônia",
        "event_type": "visita",
        "offset_days": 30,
    },
    {
        "title": "Reunião final com fornecedores",
        "event_type": "reuniao",
        "offset_days": 7,
    },
]

# ── Template: Praia 6 meses ─────────────────────────────────────────────

BEACH_6M_TEMPLATE: list[dict[str, Any]] = [
    {
        "title": "Definir local na praia",
        "event_type": "visita",
        "offset_days": 180,
    },
    {
        "title": "Contratar celebrante",
        "event_type": "reuniao",
        "offset_days": 160,
    },
    {
        "title": "Prova do vestido de noiva",
        "event_type": "visita",
        "offset_days": 150,
    },
    {
        "title": "Degustação do buffet",
        "event_type": "degustacao",
        "offset_days": 120,
    },
    {
        "title": "Escolher decoração praiana",
        "event_type": "outro",
        "offset_days": 90,
    },
    {
        "title": "Reunião com cerimonial",
        "event_type": "reuniao",
        "offset_days": 60,
    },
    {
        "title": "Ensaio geral",
        "event_type": "visita",
        "offset_days": 14,
    },
    {
        "title": "Reunião final com fornecedores",
        "event_type": "reuniao",
        "offset_days": 7,
    },
]

# ── Template: Civil + Buffet 3 meses ────────────────────────────────────

CIVIL_BUFFET_3M_TEMPLATE: list[dict[str, Any]] = [
    {
        "title": "Contratar celebrante",
        "event_type": "reuniao",
        "offset_days": 90,
    },
    {
        "title": "Definir local do buffet",
        "event_type": "visita",
        "offset_days": 75,
    },
    {
        "title": "Degustação do buffet",
        "event_type": "degustacao",
        "offset_days": 60,
    },
    {
        "title": "Escolher decoração",
        "event_type": "outro",
        "offset_days": 45,
    },
    {
        "title": "Reunião com cerimonial",
        "event_type": "reuniao",
        "offset_days": 30,
    },
    {
        "title": "Ensaio geral",
        "event_type": "visita",
        "offset_days": 7,
    },
    {
        "title": "Reunião final",
        "event_type": "reuniao",
        "offset_days": 3,
    },
]

# ── Registry ────────────────────────────────────────────────────────────

TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "religious_12m": RELIGIOUS_12M_TEMPLATE,
    "beach_6m": BEACH_6M_TEMPLATE,
    "civil_buffet_3m": CIVIL_BUFFET_3M_TEMPLATE,
}

TEMPLATE_CHOICES: list[str] = list(TEMPLATES.keys())


def get_template_events(template_name: str) -> list[dict[str, Any]]:
    """
    Retorna a lista de eventos pré-definidos do template solicitado.

    Args:
        template_name: O nome identificador do template de cronograma.

    Returns:
        Lista contendo dicionários representativos dos eventos do template,
        com as chaves `title`, `event_type` e `offset_days`.

    Raises:
        BusinessRuleViolation: Se o template solicitado não for encontrado.
    """
    template = TEMPLATES.get(template_name)
    if template is None:
        raise BusinessRuleViolation(
            detail=(
                f"Template '{template_name}' não encontrado. "
                f"Opções disponíveis: {', '.join(TEMPLATE_CHOICES)}"
            ),
            code="template_not_found",
        )
    return [dict(e) for e in template]
