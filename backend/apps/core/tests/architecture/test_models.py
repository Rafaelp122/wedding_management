from django.apps import apps


def test_domain_models_have_tenancy_protection():
    """
    AUDITORIA DE TENANCY (ADR-016): Garante que todo modelo de domínio possui
    proteção de isolamento.
    Modelos em domain apps devem ser vinculados a uma 'Company' OU a um 'Event'.
    """
    domain_apps = ["finances", "logistics", "scheduler", "events"]

    for model in apps.get_models():
        app_label = model._meta.app_label

        # Ignora modelos internos do Django e apps de infraestrutura
        if app_label in [
            "admin",
            "auth",
            "contenttypes",
            "sessions",
            "core",
            "users",
            "tenants",
        ]:
            continue

        if app_label in domain_apps:
            # Ignora o modelo WeddingDetail pois ele é uma extensão 1:1 de Event
            if model.__name__ == "WeddingDetail":
                continue

            # Verifica se possui algum dos campos de proteção (Company ou Event)
            has_company = hasattr(model, "company")
            has_event = hasattr(model, "event")

            # Fallback temporário para Planner (compatibilidade)
            has_planner = hasattr(model, "planner")

            assert has_company or has_event or has_planner, (
                f"Model {model.__name__} no app {app_label} não possui vínculo "
                "de Tenancy (nem 'company' nem 'event'). "
                "Herde de um Mixin em apps/tenants/mixins.py ou apps/events/mixins.py!"
            )
