"""
Fábricas do domínio de clientes (Client Factories).
"""

from typing import Any

import factory

from apps.clients.models import Client
from apps.tenants.tests.factories import CompanyFactory


class ClientFactory(factory.django.DjangoModelFactory):
    """Fábrica para geração de instâncias de Client para testes."""

    class Meta:
        model = Client

    company = factory.SubFactory(CompanyFactory)
    name: Any = factory.Faker("name", locale="pt_BR")
    cpf: str = factory.Sequence(lambda n: f"{n:011d}"[:11])
    email: Any = factory.Faker("email")
    phone: str = "(11) 98765-4321"
    notes: str = ""
