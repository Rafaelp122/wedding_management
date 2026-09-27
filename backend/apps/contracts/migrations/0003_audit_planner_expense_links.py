

from __future__ import annotations

from typing import Any

from django.db import migrations


def audit_planner_expense_links(apps: Any, schema_editor: Any) -> None:
    """
    Audita e repara vínculos Expense <-> Contract PLANNER (Onda 3 / RFC-001).

    Contexto: a migração 0002 religa despesas de honorários ao novo contrato
    PLANNER por `name__icontains='Honorários'`, o que é frágil (acentos,
    homônimos, colisão OneToOne). Esta migração é idempotente e conservadora:
    só vincula quando existe EXATAMENTE UM candidato órfão no mesmo
    (company, wedding); nos demais casos apenas registra aviso para
    conciliação manual. Nunca desvincula nem sobrescreve vínculo existente.
    """
    import logging

    logger = logging.getLogger(__name__)

    NewContract = apps.get_model("contracts", "Contract")
    Expense = apps.get_model("finances", "Expense")

    repaired = 0
    warnings = 0

    planners = NewContract.objects.filter(contract_type="PLANNER")
    for planner in planners.iterator():
        linked = Expense.objects.filter(contract_id=planner.id).first()
        if linked is not None:
            if linked.wedding_id != planner.wedding_id:
                logger.warning(
                    "Despesa %s vinculada ao PLANNER %s com wedding divergente "
                    "(despesa wedding_id=%s, contrato wedding_id=%s). "
                    "Conciliação manual necessária.",
                    linked.id,
                    planner.uuid,
                    linked.wedding_id,
                    planner.wedding_id,
                )
                warnings += 1
            continue

        candidates = list(
            Expense.objects.filter(
                company_id=planner.company_id,
                wedding_id=planner.wedding_id,
                contract__isnull=True,
                name__icontains="Honorários",
            )
        )
        if len(candidates) == 1:
            candidates[0].contract_id = planner.id
            candidates[0].save(update_fields=["contract"])
            repaired += 1
        elif candidates:
            logger.warning(
                "PLANNER %s (wedding_id=%s) sem despesa vinculada e com %d "
                "despesas 'Honorários' órfãs candidatas. "
                "Vínculo ambíguo: conciliação manual necessária.",
                planner.uuid,
                planner.wedding_id,
                len(candidates),
            )
            warnings += 1

    logger.info(
        "Auditoria de vínculos PLANNER/Expense concluída: "
        "%d reparados, %d avisos.",
        repaired,
        warnings,
    )


def reverse_noop(apps: Any, schema_editor: Any) -> None:
    """Irreversível por design: auditoria nunca desfaz vínculos legítimos."""


class Migration(migrations.Migration):

    dependencies = [
        ("contracts", "0002_migrate_contract_data"),
        ("finances", "0004_alter_expense_contract"),
    ]

    operations = [
        migrations.RunPython(
            audit_planner_expense_links,
            reverse_code=reverse_noop,
        ),
    ]
