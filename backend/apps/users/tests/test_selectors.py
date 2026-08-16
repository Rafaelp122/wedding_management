"""
Testes para os seletores do domínio de Usuários.
"""

from typing import Any, cast
from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory
from apps.users.models import User
from apps.users.selectors import (
    user_get_by_email_selector,
    user_get_by_uuid_selector,
    user_list_selector,
)
from apps.users.tests.factories import UserFactory as _UserFactory


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


@pytest.mark.django_db
class TestUserGetByEmailSelector:
    """Testes para o seletor user_get_by_email_selector."""

    def test_get_by_email_success(self) -> None:
        user = UserFactory(email="teste@exemplo.com")
        result = user_get_by_email_selector(email="teste@exemplo.com")
        assert result.id == user.id

    def test_get_by_email_normalized_case(self) -> None:
        user = UserFactory(email="usuario@exemplo.com")
        result = user_get_by_email_selector(email="USUARIO@EXEMPLO.COM")
        assert result.id == user.id

    def test_get_by_email_not_found_raises_object_not_found(self) -> None:
        with pytest.raises(ObjectNotFoundError):
            user_get_by_email_selector(email="inexistente@exemplo.com")


@pytest.mark.django_db
class TestUserGetByUuidSelector:
    """Testes para o seletor user_get_by_uuid_selector."""

    def test_get_by_uuid_instance_success(self) -> None:
        user = UserFactory()
        result = user_get_by_uuid_selector(uuid=user.uuid)
        assert result.id == user.id

    def test_get_by_uuid_string_success(self) -> None:
        user = UserFactory()
        result = user_get_by_uuid_selector(uuid=str(user.uuid))
        assert result.id == user.id

    def test_get_by_uuid_not_found_raises_object_not_found(self) -> None:
        with pytest.raises(ObjectNotFoundError):
            user_get_by_uuid_selector(uuid=uuid4())


@pytest.mark.django_db
class TestUserListSelector:
    """Testes para o seletor user_list_selector."""

    def test_user_list_all_users(self) -> None:
        u1 = UserFactory()
        u2 = UserFactory()

        qs = user_list_selector()
        ids = {u.id for u in qs}
        assert u1.id in ids
        assert u2.id in ids

    def test_user_list_filtered_by_company(self) -> None:
        company_a = CompanyFactory()
        company_b = CompanyFactory()

        u_a1 = UserFactory(company=company_a)
        u_a2 = UserFactory(company=company_a)
        u_b = UserFactory(company=company_b)

        qs = user_list_selector(company=company_a)
        assert qs.count() == 2
        ids = {u.id for u in qs}
        assert u_a1.id in ids
        assert u_a2.id in ids
        assert u_b.id not in ids
