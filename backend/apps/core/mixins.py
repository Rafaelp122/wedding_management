from django.conf import settings
from django.db import models


class PlannerOwnedMixin(models.Model):
    """
    Mixin para modelos que pertencem globalmente a um Planner.

    Deve ser utilizado em recursos que o Planner gerencia de forma transversal
    a vários casamentos, como catálogos de fornecedores ou configurações personalizadas.
    """

    planner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        # O uso de %(class)s evita colisões de related_name em heranças múltiplas
        related_name="%(class)s_records",
        verbose_name="Planner Responsável",
        help_text="Identifica o Planner dono deste registro para isolamento de dados.",
    )

    class Meta:
        abstract = True


class WeddingOwnedMixin(models.Model):
    """
    Mixin para modelos vinculados a um contexto de Casamento específico.

    Essencial para recursos de logística e planejamento (Convidados, Tarefas,
    Orçamentos e etc...).
    O isolamento final é feito via 'wedding__planner' no BaseViewSet (ADR-009).
    """

    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.CASCADE,
        # Garante que possamos acessar registros a partir do objeto Wedding
        related_name="%(class)s_records",
        verbose_name="Casamento",
        help_text="Vincula o registro a um evento específico gerenciado pelo Planner.",
    )

    class Meta:
        abstract = True
