from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0003_event_source_installment'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Task',
            new_name='ChecklistItem',
        ),
        migrations.AlterModelOptions(
            name='checklistitem',
            options={
                'ordering': ['is_completed', 'due_date', 'created_at'],
                'verbose_name': 'Item de Checklist',
                'verbose_name_plural': 'Itens de Checklist',
            },
        ),
        migrations.AlterModelTable(
            name='checklistitem',
            table='scheduler_task',
        ),
        migrations.AddField(
            model_name='checklistitem',
            name='priority',
            field=models.CharField(
                choices=[('LOW', 'Baixa'), ('MEDIUM', 'Média'), ('HIGH', 'Alta'), ('URGENT', 'Urgente')],
                default='MEDIUM',
                max_length=20,
                verbose_name='Prioridade',
            ),
        ),
        migrations.AddField(
            model_name='checklistitem',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data de Conclusão'),
        ),
        migrations.AddIndex(
            model_name='checklistitem',
            index=models.Index(fields=['company', 'priority'], name='scheduler_t_company_45611c_idx'),
        ),
    ]
