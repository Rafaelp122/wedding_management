"""
Fábricas de Utilizadores (User Factories).

Este ficheiro define os blueprints para geração de Planners e Administradores.
É o componente central para testes de autenticação e isolamento de dados.

Destaques Técnicos:
- Password Padrão: 'password123' (definida no método _create).
- UserManager: Utiliza o 'create_user' customizado para garantir o hashing da senha.
- Unicidade: Garante emails únicos para evitar conflitos de integridade no PostgreSQL.
"""

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

    # Gera emails únicos: planner0@example.com, planner1@example.com...
    # Essencial para evitar erros de integridade no seu modelo
    email = factory.Sequence(lambda n: f"planner{n}@example.com")

    # Usa o Faker configurado como pt_BR (no conftest global) para nomes reais
    name = factory.Faker("name")

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
