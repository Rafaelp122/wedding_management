import logging
from typing import Any

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import DomainIntegrityError
from apps.core.types import AuthContextUser
from apps.finances.models import BudgetCategory
from apps.logistics.models import Contract, Supplier
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class ContractService:
    """
    Camada de serviço para gestão de contratos.
    """

    @staticmethod
    def list(user: AuthContextUser, wedding_id: Any = None) -> QuerySet[Contract]:
        qs = Contract.objects.for_user(user).select_related(
            "supplier", "wedding", "budget_category"
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Contract:
        planner = require_user(user)
        logger.info(f"Iniciando criação de Contrato para planner_id={planner.id}")

        # Resolução de dependências via Resolvers genéricos (Pureza de Segurança)
        wedding = Wedding.objects.resolve(planner, data.pop("wedding"))
        supplier = Supplier.objects.resolve(planner, data.pop("supplier"))

        category_uuid = data.pop("budget_category", None)
        budget_category = (
            BudgetCategory.objects.resolve(planner, category_uuid)
            if category_uuid
            else None
        )

        contract = Contract(
            wedding=wedding, supplier=supplier, budget_category=budget_category, **data
        )
        contract.save()

        logger.info(f"Contrato criado com sucesso: uuid={contract.uuid}")
        return contract

    @staticmethod
    @transaction.atomic
    def update(
        user: AuthContextUser, instance: Contract, data: dict[str, Any]
    ) -> Contract:
        """
        Atualiza uma instância de contrato resolvendo chaves estrangeiras.
        """
        planner = require_user(user)
        logger.info(f"Atualizando Contrato uuid={instance.uuid}")

        # Proteção contra sequestro de contexto
        data.pop("wedding", None)
        data.pop("planner", None)

        # Resolução de Fornecedor se fornecido no payload
        if "supplier" in data:
            instance.supplier = Supplier.objects.resolve(planner, data.pop("supplier"))

        # Resolução de Categoria de Orçamento se fornecido no payload
        if "budget_category" in data:
            category_uuid = data.pop("budget_category")
            instance.budget_category = (
                BudgetCategory.objects.resolve(planner, category_uuid)
                if category_uuid
                else None
            )

        for field, value in data.items():
            if field == "pdf_file" and value is None:
                continue
            setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Contract) -> None:
        """
        Deleta uma instância de contrato.
        """
        logger.info(f"Tentativa de deleção do Contrato uuid={instance.uuid}")
        instance.items.update(contract=None)

        try:
            instance.delete()
        except ProtectedError as e:
            raise DomainIntegrityError(
                detail="Não é possível apagar este contrato pois existem registros "
                "financeiros vinculados a ele.",
                code="contract_protected_error",
            ) from e
