"""
Classe base para testes de arquitetura e isolamento multi-tenant.

Este módulo define a classe BaseTenantIsolationTest com utilitários e asserções
para garantir que modelos do sistema respeitam o isolamento por empresa (company)
tanto na camada de ORM (for_tenant) quanto nos atalhos de consulta
(get_object_or_404_for_tenant).
"""

from typing import Any, ClassVar, cast

import factory
import pytest
from django.db import models

from apps.core.exceptions import ObjectNotFoundError
from apps.core.shortcuts import get_object_or_404_for_tenant, resolve_tenant_resource
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class BaseTenantIsolationTest:
    """
    Classe base reutilizável para validação de isolamento multi-tenant de modelos.

    Fornece métodos helpers que instanciam recursos via factories para duas
    empresas distintas (Company A e Company B) e realizam as verificações
    de segurança vertical.
    """

    model_class: ClassVar[type[models.Model] | None] = None
    factory_class: ClassVar[type[factory.django.DjangoModelFactory[Any]] | None] = None

    def create_company(self) -> Company:
        """
        Cria e retorna uma nova empresa utilizando a CompanyFactory.

        Returns:
            Instância de Company criada para o teste.
        """
        return cast(Company, CompanyFactory())

    def create_factory_instance(
        self,
        factory_cls: type[factory.django.DjangoModelFactory[Any]],
        company: Company,
        **kwargs: Any,
    ) -> models.Model:
        """
        Instancia um objeto de modelo vinculado a uma empresa específica.

        Caso o modelo possua o campo 'wedding' (WeddingOwnedMixin) e este não tenha
        sido informado via kwargs, cria automaticamente um casamento associado à mesma
        empresa para manter a integridade relacional.

        Args:
            factory_cls: Classe da fábrica (FactoryBoy) do modelo.
            company: Instância da empresa dona do recurso.
            **kwargs: Atributos adicionais para a fábrica.

        Returns:
            Instância do modelo salva no banco de dados.
        """
        model_cls = factory_cls._meta.model
        params: dict[str, Any] = {}

        if factory_cls.__name__ == "ExpenseFactory" and "category" not in kwargs:
            from apps.finances.tests.factories import BudgetCategoryFactory

            wedding = kwargs.get("wedding") or WeddingFactory(company=company)
            category = BudgetCategoryFactory(company=company, wedding=wedding)
            params["wedding"] = wedding
            params["category"] = category
            params["company"] = company
        elif factory_cls.__name__ == "InstallmentFactory" and "expense" not in kwargs:
            from apps.finances.tests.factories import (
                BudgetCategoryFactory,
                ExpenseFactory,
            )

            wedding = kwargs.get("wedding") or WeddingFactory(company=company)
            category = BudgetCategoryFactory(company=company, wedding=wedding)
            expense = ExpenseFactory(
                company=company, wedding=wedding, category=category
            )
            params["wedding"] = wedding
            params["expense"] = expense
            params["company"] = company
        elif hasattr(model_cls, "wedding") and "wedding" not in kwargs:
            wedding = WeddingFactory(company=company)
            params["wedding"] = wedding
        elif "company" not in kwargs:
            params["company"] = company

        params.update(kwargs)
        return cast(models.Model, factory_cls(**params))

    def assert_for_tenant_isolation(
        self,
        model_cls: type[models.Model],
        factory_cls: type[factory.django.DjangoModelFactory[Any]],
    ) -> None:
        """
        Valida que Model.objects.for_tenant(company) filtra rigorosamente por tenant.

        Cria objetos para duas empresas diferentes (Company A e Company B) e garante
        que a consulta for_tenant de uma empresa nunca retorna objetos da outra.

        Args:
            model_cls: Classe do modelo Django a ser testado.
            factory_cls: Classe da fábrica para o modelo.
        """
        company_a = self.create_company()
        company_b = self.create_company()

        obj_a = self.create_factory_instance(factory_cls, company_a)
        obj_b = self.create_factory_instance(factory_cls, company_b)

        qs_a = model_cls.objects.for_tenant(company_a)  # type: ignore[attr-defined]
        qs_b = model_cls.objects.for_tenant(company_b)  # type: ignore[attr-defined]

        assert obj_a in qs_a, (
            f"Objeto {obj_a} deveria estar presente nas consultas da Empresa A."
        )
        assert obj_b not in qs_a, (
            f"Vazamento de dados: Objeto {obj_b} da Empresa B retornado na Empresa A."
        )

        assert obj_b in qs_b, (
            f"Objeto {obj_b} deveria estar presente nas consultas da Empresa B."
        )
        assert obj_a not in qs_b, (
            f"Vazamento de dados: Objeto {obj_a} da Empresa A retornado na Empresa B."
        )

    def assert_get_object_or_404_for_tenant_isolation(
        self,
        model_cls: type[models.Model],
        factory_cls: type[factory.django.DjangoModelFactory[Any]],
    ) -> None:
        """
        Valida que get_object_or_404_for_tenant nega acesso cross-tenant com 404.

        Garante que tentar recuperar um objeto de Company A usando Company B
        lança a exceção ObjectNotFoundError (que é traduzida para HTTP 404).

        Args:
            model_cls: Classe do modelo Django a ser testado.
            factory_cls: Classe da fábrica para o modelo.
        """
        company_a = self.create_company()
        company_b = self.create_company()

        obj_a = self.create_factory_instance(factory_cls, company_a)

        # Acesso válido pela empresa proprietária
        resolved = get_object_or_404_for_tenant(model_cls, company_a, obj_a.uuid)  # type: ignore[attr-defined]
        assert resolved == obj_a

        # Tentativa de acesso indevido por outra empresa
        with pytest.raises(ObjectNotFoundError) as exc_info:
            get_object_or_404_for_tenant(model_cls, company_b, obj_a.uuid)  # type: ignore[attr-defined]

        assert exc_info.value.code == "not_found_or_denied"

    def assert_resolve_tenant_resource_isolation(
        self,
        model_cls: type[models.Model],
        factory_cls: type[factory.django.DjangoModelFactory[Any]],
    ) -> None:
        """
        Valida que resolve_tenant_resource bloqueia acessos cross-tenant.

        Testa tanto a resolução por UUID quanto por referência direta de instância.

        Args:
            model_cls: Classe do modelo Django a ser testado.
            factory_cls: Classe da fábrica para o modelo.
        """
        company_a = self.create_company()
        company_b = self.create_company()

        obj_a = self.create_factory_instance(factory_cls, company_a)

        # Resolução por UUID válida
        res_uuid = resolve_tenant_resource(model_cls, company_a, obj_a.uuid)  # type: ignore[attr-defined]
        assert res_uuid == obj_a

        # Resolução por instância válida
        res_inst = resolve_tenant_resource(model_cls, company_a, obj_a)
        assert res_inst == obj_a

        # Negação por UUID na empresa errada
        with pytest.raises(ObjectNotFoundError):
            resolve_tenant_resource(model_cls, company_b, obj_a.uuid)  # type: ignore[attr-defined]

        # Negação por instância na empresa errada
        with pytest.raises(ObjectNotFoundError):
            resolve_tenant_resource(model_cls, company_b, obj_a)

    def assert_tenant_isolation(
        self,
        model_cls: type[models.Model],
        factory_cls: type[factory.django.DjangoModelFactory[Any]],
    ) -> None:
        """
        Executa a suíte completa de testes de isolamento multi-tenant para um modelo.

        Args:
            model_cls: Classe do modelo Django a ser validado.
            factory_cls: Fábrica (FactoryBoy) do modelo.
        """
        self.assert_for_tenant_isolation(model_cls, factory_cls)
        self.assert_get_object_or_404_for_tenant_isolation(model_cls, factory_cls)
        self.assert_resolve_tenant_resource_isolation(model_cls, factory_cls)
