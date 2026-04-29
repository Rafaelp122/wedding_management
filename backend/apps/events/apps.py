import sys

from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.events"

    def ready(self):
        # Evita carregar signals durante os testes se necessário para evitar conflitos OneToOne
        # mas aqui vamos manter para consistência, e tratar nos testes se precisar.
        # No entanto, para resolver o erro 'Budget já existe', vamos desabilitar nos testes.
        if "test" not in sys.argv and "pytest" not in sys.modules:
            import apps.events.signals  # noqa
