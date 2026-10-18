"""
Seletores de leitura para o domínio de Usuários.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import QuerySet

from apps.core.exceptions import ObjectNotFoundError
from apps.users.models import User


if TYPE_CHECKING:
    from apps.tenants.models import Company


def user_get_by_email_selector(*, email: str) -> User:
    """Recupera um usuário pelo endereço de e-mail normalizado.

    Decisão Arquitetural: [ADR-016](docs/architecture/adr/016-pragmatic-multi-tenancy.md)

    Raises:
        ObjectNotFoundError: Se nenhum usuário for encontrado com o e-mail fornecido.
    """
    normalized_email = User.objects.normalize_email(email.strip().lower())
    user = User.objects.filter(email__iexact=normalized_email).first()
    if not user:
        raise ObjectNotFoundError(
            detail=f"Usuário não encontrado com e-mail '{email}'."
        )
    return user


def user_get_by_uuid_selector(*, uuid: UUID | str) -> User:
    """Recupera um usuário pelo seu identificador público UUID.

    Decisão Arquitetural: [ADR-016](docs/architecture/adr/016-pragmatic-multi-tenancy.md)

    Raises:
        ObjectNotFoundError: Se nenhum usuário for encontrado com o UUID fornecido.
    """
    user = User.objects.filter(uuid=uuid).first()
    if not user:
        raise ObjectNotFoundError(detail=f"Usuário não encontrado com UUID '{uuid}'.")
    return user


def user_list_selector(*, company: Company | None = None) -> QuerySet[User]:
    """Lista usuários do sistema com filtro opcional por empresa (tenant).

    Decisão Arquitetural: [ADR-016](docs/architecture/adr/016-pragmatic-multi-tenancy.md)
    """
    qs = User.objects.all()
    if company is not None:
        qs = qs.filter(company=company)
    return qs
