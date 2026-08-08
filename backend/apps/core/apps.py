from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self) -> None:
        """Executa a auto-descoberta de módulos cron.py em todos os INSTALLED_APPS."""
        autodiscover_modules("cron")
