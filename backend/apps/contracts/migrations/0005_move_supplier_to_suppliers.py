import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0004_move_supplier_from_logistics'),
        ('suppliers', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveIndex(
                    model_name='supplier',
                    name='logistics_s_company_c0f8da_idx',
                ),
                migrations.RemoveIndex(
                    model_name='supplier',
                    name='logistics_s_is_acti_388f6b_idx',
                ),
                migrations.RemoveIndex(
                    model_name='supplier',
                    name='logistics_s_city_41e037_idx',
                ),
                migrations.AlterField(
                    model_name='contract',
                    name='supplier',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='contracts',
                        to='suppliers.supplier',
                        verbose_name='Fornecedor',
                    ),
                ),
                migrations.DeleteModel(
                    name='Supplier',
                ),
            ],
            database_operations=[],
        ),
    ]
