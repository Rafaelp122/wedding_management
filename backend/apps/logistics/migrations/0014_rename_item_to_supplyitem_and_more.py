from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0013_remove_contract_parent'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Item',
            new_name='SupplyItem',
        ),
        migrations.AlterModelOptions(
            name='supplyitem',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Item de Suprimento',
                'verbose_name_plural': 'Itens de Suprimento',
            },
        ),
        migrations.AlterModelTable(
            name='supplyitem',
            table='logistics_item',
        ),
        migrations.AddField(
            model_name='supplyitem',
            name='scope_status',
            field=models.CharField(
                choices=[('DESIRED', 'Desejado'), ('INCLUDED', 'Incluído'), ('DISCARDED', 'Descartado')],
                default='INCLUDED',
                max_length=20,
                verbose_name='Status de Escopo',
            ),
        ),
        migrations.AddField(
            model_name='supplyitem',
            name='rejection_reason',
            field=models.TextField(
                blank=True,
                default='',
                verbose_name='Motivo do Descarte',
            ),
        ),
        migrations.AddField(
            model_name='supplyitem',
            name='procurement_status',
            field=models.CharField(
                choices=[('A_COTAR', 'A Cotar'), ('EM_NEGOCIACAO', 'Em Negociação'), ('CONTRATADO', 'Contratado')],
                default='CONTRATADO',
                max_length=20,
                verbose_name='Status de Cotação',
            ),
        ),
        migrations.AddField(
            model_name='supplyitem',
            name='delivery_status',
            field=models.CharField(
                choices=[('PENDING', 'Pendente'), ('DELIVERED', 'Entregue'), ('RETURNED', 'Devolvido')],
                default='PENDING',
                max_length=20,
                verbose_name='Status de Entrega Física',
            ),
        ),
        migrations.AddIndex(
            model_name='supplyitem',
            index=models.Index(fields=['company', 'scope_status'], name='logistics_i_company_b44d30_idx'),
        ),
        migrations.AddIndex(
            model_name='supplyitem',
            index=models.Index(fields=['company', 'delivery_status'], name='logistics_i_company_81b453_idx'),
        ),
    ]
