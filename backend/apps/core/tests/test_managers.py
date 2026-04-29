import pytest
from django.db import models

from apps.core.models import BaseModel
from apps.tenants.mixins import CompanyOwnedMixin
from apps.users.tests.factories import UserFactory


class ManagerMockModel(BaseModel, CompanyOwnedMixin):
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
        """Garante que for_user() retorna apenas registros da empresa do usuário."""
        other_user = UserFactory()

        # Registros da empresa do usuário alvo
        ManagerMockModel.objects.create(company=user.company, title="T1")
        ManagerMockModel.objects.create(company=user.company, title="T2")

        # Registro de outra empresa
        ManagerMockModel.objects.create(company=other_user.company, title="T3")

        # Execução
        queryset = ManagerMockModel.objects.for_user(user)

        # Asserções
        assert queryset.count() == 2
        assert all(m.company == user.company for m in queryset)

    def test_for_user_returns_empty_for_user_without_data(self, user):
        """Garante que retorna queryset vazio se a empresa não possuir registros."""
        other_user = UserFactory()
        ManagerMockModel.objects.create(company=other_user.company, title="T1")

        queryset = ManagerMockModel.objects.for_user(user)

        assert queryset.count() == 0

    def test_for_anonymous_user_returns_none(self):
        """Garante que para usuário anônimo o retorno é vazio (segurança)."""
        from django.contrib.auth.models import AnonymousUser

        other_user = UserFactory()

        ManagerMockModel.objects.create(company=other_user.company, title="T1")

        queryset = ManagerMockModel.objects.for_user(AnonymousUser())

        assert queryset.count() == 0
