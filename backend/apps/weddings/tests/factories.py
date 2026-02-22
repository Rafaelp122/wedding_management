"""
Fábricas de Casamentos (Wedding Factories).

Este ficheiro define os blueprints para geração de Casamentos (Tenants).
É fundamental para testar o isolamento de dados (Multitenancy) e as regras
de ciclo de vida do evento.

Destaques Técnicos:
- Planner Automático: Vincula cada casamento a um novo User (Planner) via SubFactory.
- Regra BR-W01: A factory padrão gera datas futuras para garantir que o status
  'IN_PROGRESS' seja válido.
- Faker pt_BR: Utiliza nomes e endereços brasileiros reais.
"""

import factory

from apps.users.tests.factories import UserFactory
from apps.weddings.models import Wedding


class WeddingPayloadFactory(factory.Factory):
    """Gera o dicionário exato que o Frontend enviaria no POST."""

    class Meta:
        model = dict  # Esta factory gera dicionários, não modelos

    bride_name = factory.Faker("first_name_female")
    groom_name = factory.Faker("first_name_male")
    date = factory.Faker("future_date")
    location = factory.Faker("address")
    total_estimated = factory.Iterator([50000, 100000, 150000])


class WeddingFactory(factory.django.DjangoModelFactory):
    """
    Fábrica para o modelo Wedding.
    Garante que cada casamento tenha um planner (User) associado.
    """

    class Meta:
        model = Wedding

    # Cria automaticamente um utilizador (Planner) se nenhum for passado
    planner = factory.SubFactory(UserFactory)

    # Dados gerados pelo Faker (pt_BR conforme definido no conftest global)
    groom_name = factory.Faker("first_name_male")
    bride_name = factory.Faker("first_name_female")

    # Define uma data no futuro para evitar erro na regra BR-W01
    date = factory.Faker("future_date")
    location = factory.Faker("address")
    expected_guests = factory.Iterator([50, 100, 150, 200])

    # Status inicial padrão conforme o modelo
    status = Wedding.StatusChoices.IN_PROGRESS

    budget = factory.RelatedFactory(
        "apps.finances.tests.model_factories.BudgetFactory",
        factory_related_name="wedding",
    )


class CompletedWeddingFactory(WeddingFactory):
    """Sub-fábrica para testar casamentos já realizados (respeita a regra BR-W01)."""

    date = factory.Faker("past_date")
    status = Wedding.StatusChoices.COMPLETED
