# Generated manually: Remove parent field from Contract

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0012_migrate_contract_addendums'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='parent',
        ),
    ]
