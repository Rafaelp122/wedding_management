from django.db import migrations


def mark_existing_users_verified(apps, schema_editor):
    user_model = apps.get_model("users", "User")
    user_model.objects.filter(is_email_verified=False).update(is_email_verified=True)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_user_email_verified_at_user_is_email_verified"),
    ]

    operations = [
        migrations.RunPython(mark_existing_users_verified, migrations.RunPython.noop),
    ]
