

from django.db import migrations


class Migration(migrations.Migration):
    """Remove o estado do modelo Supplier da logistics (mudou para contracts).

    State-only: a tabela `logistics_supplier` e seus dados permanecem
    intactos — apenas o registro do modelo troca de app (ver
    `contracts/0004_move_supplier_from_logistics`).
    """

    dependencies = [
        ("contracts", "0004_move_supplier_from_logistics"),
        ("logistics", "0015_alter_supplyitem_contract_and_delete_legacy_contract"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name="Supplier",
                ),
            ],
            database_operations=[],
        ),
    ]
