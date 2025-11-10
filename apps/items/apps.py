from django.apps import AppConfig


class ItemsConfig(AppConfig):
    # Configuração do app de itens
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.items"

    def ready(self):
        # Importa os signals quando o app é carregado
        import apps.items.signals
