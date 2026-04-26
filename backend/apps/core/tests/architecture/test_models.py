from django.apps import apps


def test_domain_models_have_tenancy_protection():
    """
    AUDITORIA DE TENANCY: Garante que todo modelo de domínio possui
    proteção de isolamento.
    Modelos em domain apps devem ser vinculados a um Wedding OU a um Planner.
    """
    domain_apps = ["finances", "logistics", "scheduler", "weddings"]

    for model in apps.get_models():
        app_label = model._meta.app_label

        # Ignora modelos internos do Django e do app Core
        if app_label in ["admin", "auth", "contenttypes", "sessions", "core", "users"]:
            continue

        if app_label in domain_apps:
            # Verifica se possui algum dos campos de proteção
            has_wedding = hasattr(model, "wedding")
            has_planner = hasattr(model, "planner")

            assert has_wedding or has_planner, (
                f"Model {model.__name__} no app {app_label} não possui vínculo "
                "de Tenancy (nem 'wedding' nem 'planner'). "
                "Herde de um Mixin em core/mixins.py!"
            )
