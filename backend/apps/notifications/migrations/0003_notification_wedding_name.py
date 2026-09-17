# Generated manually for ADR-031 Bounded Contexts isolation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0002_notification_target_id_notification_target_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="wedding_name",
            field=models.CharField(
                blank=True,
                null=True,
                default=None,
                max_length=255,
                verbose_name="Nome do Casamento",
            ),
        ),
    ]
