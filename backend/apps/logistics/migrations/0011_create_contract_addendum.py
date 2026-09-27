# Generated manually for ContractAddendum model (ADR-030 / RFC-001)

import apps.core.validators
import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0010_alter_contract_pdf_file'),
        ('tenants', '0001_initial'),
        ('weddings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractAddendum',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor do Aditivo')),
                ('signed_date', models.DateField(blank=True, null=True, verbose_name='Data da Assinatura')),
                ('justification', models.TextField(verbose_name='Justificativa do Aditivo')),
                ('pdf_file', models.FileField(blank=True, help_text='Formatos aceitos: PDF, PNG, JPEG. Tamanho máximo: 10MB.', null=True, upload_to='contracts/addendums/%Y/%m/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg'], message='Tipo de arquivo não suportado. Use PDF, PNG ou JPEG.'), apps.core.validators.MaxFileSizeValidator(10485760)], verbose_name='Arquivo PDF do Aditivo')),
                ('status', models.CharField(choices=[('PENDING', 'Pendente'), ('SIGNED', 'Assinado'), ('CANCELED', 'Cancelado')], default='PENDING', max_length=20)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_records', to='tenants.company', verbose_name='Empresa')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addendums', to='logistics.contract', verbose_name='Contrato Principal')),
                ('wedding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_records', to='weddings.wedding')),
            ],
            options={
                'verbose_name': 'Termo Aditivo',
                'verbose_name_plural': 'Termos Aditivos',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['company', 'wedding'], name='logistics_c_company_c1226c_idx'),
                    models.Index(fields=['contract'], name='logistics_c_contrac_af5139_idx'),
                    models.Index(fields=['status'], name='logistics_c_status_d8c1d7_idx'),
                ],
            },
        ),
    ]
