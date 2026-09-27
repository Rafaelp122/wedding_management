# Generated manually for Data Migration: transfer contracts with parent_id to ContractAddendum

from django.db import migrations


def forward_migrate_addendums(apps, schema_editor):
    Contract = apps.get_model("logistics", "Contract")
    ContractAddendum = apps.get_model("logistics", "ContractAddendum")

    parented_contracts = Contract.objects.filter(parent__isnull=False)
    for c in parented_contracts:
        status_val = c.status
        if status_val not in ["PENDING", "SIGNED", "CANCELED"]:
            status_val = "PENDING"

        ContractAddendum.objects.create(
            uuid=c.uuid,
            company=c.company,
            wedding=c.wedding,
            contract=c.parent,
            amount=c.total_amount,
            signed_date=c.signed_date,
            justification=c.description or "Migrado do contrato aditivo anterior",
            pdf_file=c.pdf_file,
            status=status_val,
        )
    # Exclui contratos que foram migrados para ContractAddendum
    parented_contracts.delete()


def reverse_migrate_addendums(apps, schema_editor):
    Contract = apps.get_model("logistics", "Contract")
    ContractAddendum = apps.get_model("logistics", "ContractAddendum")

    for a in ContractAddendum.objects.all():
        Contract.objects.create(
            uuid=a.uuid,
            company=a.company,
            wedding=a.wedding,
            supplier=a.contract.supplier,
            parent=a.contract,
            total_amount=a.amount,
            signed_date=a.signed_date,
            description=a.justification,
            pdf_file=a.pdf_file,
            status=a.status,
            name=f"Aditivo - {a.contract.name}",
        )
    ContractAddendum.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0011_create_contract_addendum'),
    ]

    operations = [
        migrations.RunPython(forward_migrate_addendums, reverse_migrate_addendums),
    ]
