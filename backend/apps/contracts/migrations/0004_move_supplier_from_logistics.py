

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


def cleanup_stale_supplier_contenttype(apps, schema_editor):
    """Remove o ContentType/Permissões órfãs de logistics.Supplier.

    O modelo mudou de app (logistics -> contracts) sem migração de dados:
    a tabela `logistics_supplier` é a mesma. O ContentType antigo apontaria
    para um modelo inexistente; o novo é criado automaticamente pelo
    post_migrate. Idempotente e reversível por recriação automática.
    """
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    stale = ContentType.objects.filter(app_label="logistics", model="supplier")
    Permission.objects.filter(content_type__in=stale).delete()
    stale.delete()


def reverse_noop(apps, schema_editor):
    """Irreversível por design: ContentTypes são recriados pelo post_migrate."""


class Migration(migrations.Migration):

    dependencies = [
        ("contracts", "0003_audit_planner_expense_links"),
        ("logistics", "0015_alter_supplyitem_contract_and_delete_legacy_contract"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Supplier",
                    fields=[
                        ("id", models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                        ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        ("name", models.CharField(help_text="Nome do fornecedor ou empresa", max_length=255, verbose_name="Nome")),
                        ("cnpj", models.CharField(blank=True, help_text="Formato: 00.000.000/0000-00", max_length=18, validators=[django.core.validators.RegexValidator(message="CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX.", regex="^(\\d{2}\\.\\d{3}\\.\\d{3}/\\d{4}-\\d{2})?$")], verbose_name="CNPJ")),
                        ("phone", models.CharField(blank=True, help_text="Formato: (00) 00000-0000", max_length=20, verbose_name="Telefone")),
                        ("email", models.EmailField(blank=True, max_length=254, verbose_name="E-mail")),
                        ("website", models.URLField(blank=True, verbose_name="Website")),
                        ("address", models.TextField(blank=True, verbose_name="Endereço")),
                        ("city", models.CharField(blank=True, max_length=100, verbose_name="Cidade")),
                        ("state", models.CharField(blank=True, max_length=2, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(2)], verbose_name="Estado (UF)")),
                        ("notes", models.TextField(blank=True, help_text="Anotações internas sobre o fornecedor", verbose_name="Observações")),
                        ("is_active", models.BooleanField(default=True, help_text="Fornecedor disponível para novos contratos", verbose_name="Ativo")),
                        ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="%(class)s_records", to="tenants.company", verbose_name="Empresa")),
                    ],
                    options={
                        "db_table": "logistics_supplier",
                        "verbose_name": "Fornecedor",
                        "verbose_name_plural": "Fornecedores",
                        "ordering": ["name"],
                    },
                ),
                migrations.AddIndex(
                    model_name="supplier",
                    index=models.Index(fields=["company", "name"], name="logistics_s_company_c0f8da_idx"),
                ),
                migrations.AddIndex(
                    model_name="supplier",
                    index=models.Index(fields=["is_active"], name="logistics_s_is_acti_388f6b_idx"),
                ),
                migrations.AddIndex(
                    model_name="supplier",
                    index=models.Index(fields=["city", "state"], name="logistics_s_city_41e037_idx"),
                ),
                migrations.AlterField(
                    model_name="contract",
                    name="supplier",
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="contracts", to="contracts.supplier", verbose_name="Fornecedor"),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    cleanup_stale_supplier_contenttype,
                    reverse_code=reverse_noop,
                ),
            ],
        ),
    ]
