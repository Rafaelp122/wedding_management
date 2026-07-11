"""
Fábricas de Utilizadores (User Factories).

Este ficheiro define os blueprints para geração de Planners e Administradores.
É o componente central para testes de autenticação e isolamento de dados.

Destaques Técnicos:
- Password Padrão: 'password123' (definida no método _create).
- UserManager: Utiliza o 'create_user' customizado para garantir o hashing da senha.
- Unicidade: Garante emails únicos para evitar conflitos de integridade no PostgreSQL.
"""

import uuid

import factory
from django.contrib.auth import get_user_model


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """
    Fábrica para o modelo User customizado.
    Gera Planners (usuários) para o sistema de gestão de casamentos.
    """

    class Meta:
        model = User

    # Vincula explicitamente a uma Company via SubFactory (cross-app).
    # A alternativa anterior (depender do CustomUserManager._create_user
    # chamar TenantService.create_company() implicitamente) era pior.
    company = factory.SubFactory("apps.tenants.tests.factories.CompanyFactory")

    # Gera emails únicos e garantidos contra colisões em execuções paralelas
    email = factory.Sequence(
        lambda n: f"planner_{n}_{uuid.uuid4().hex[:8]}@example.com"
    )

    # Usa o Faker configurado como pt_BR (no conftest global) para nomes reais
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    # No modelo o padrão é False, mas para testes a maioria dos fluxos
    # exige um usuário ativo para passar pelo JWT
    is_active = True
    is_staff = False
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Sobrescreve a criação para usar o CustomUserManager.
        Isso garante que a senha seja criptografada via set_password().
        """
        password = kwargs.pop("password", "password123")
        manager = cls._get_manager(model_class)
        # Usa o create_user definido no seu CustomUserManager
        return manager.create_user(*args, password=password, **kwargs)


class AdminFactory(UserFactory):
    """Fábrica para criação rápida de superusuários ativos."""

    is_staff = True
    is_superuser = True
