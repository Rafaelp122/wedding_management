import pytest
from django.db import models

from apps.core.mixins import PlannerOwnedMixin
from apps.core.models import BaseModel
from apps.users.tests.factories import UserFactory


class ManagerMockModel(BaseModel, PlannerOwnedMixin):
    """Modelo mock para testar o Manager."""

    title = models.CharField(max_length=100)

    class Meta:
        app_label = "core"


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.multitenancy
class TestBaseManager:
    """Testes para o isolamento de dados via Manager."""

    def test_for_user_filters_correctly(self, user):
        """Garante que for_user() retorna apenas registros do usuário fornecido."""
        other_user = UserFactory()

        # Registros do usuário alvo
        ManagerMockModel.objects.create(planner=user, title="T1")
        ManagerMockModel.objects.create(planner=user, title="T2")

        # Registro de outro usuário
        ManagerMockModel.objects.create(planner=other_user, title="T3")

        # Execução
        queryset = ManagerMockModel.objects.for_user(user)

        # Asserções
        assert queryset.count() == 2
        assert all(m.planner == user for m in queryset)

    def test_for_user_returns_empty_for_user_without_data(self, user):
        """Garante que retorna queryset vazio se o usuário não possuir registros."""
        other_user = UserFactory()
        ManagerMockModel.objects.create(planner=other_user, title="T1")

        queryset = ManagerMockModel.objects.for_user(user)

        assert queryset.count() == 0

    def test_for_anonymous_user_returns_none(self):
        """Garante que para usuário anônimo o retorno é vazio (segurança)."""
        from django.contrib.auth.models import AnonymousUser

        ManagerMockModel.objects.create(planner=UserFactory(), title="T1")

        queryset = ManagerMockModel.objects.for_user(AnonymousUser())

        assert queryset.count() == 0
