import logging
from typing import Any

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import (
    DomainIntegrityError,
)
from apps.core.types import AuthContextUser
from apps.logistics.models import Supplier


logger = logging.getLogger(__name__)


class SupplierService:
    """
    Camada de serviço para gestão de fornecedores.
    Centraliza a lógica de catálogo transversal ao Planner (RF09).
    Garante auditoria, validação estrita via Model e tratamento de integridade
    referencial.
    """

    @staticmethod
    def list(user: AuthContextUser) -> QuerySet[Supplier]:
        return Supplier.objects.for_user(user)

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Supplier:
        planner = require_user(user)
        logger.info(f"Iniciando criação de Fornecedor para planner_id={planner.id}")

        # O full_clean() é chamado automaticamente no save() do BaseModel
        supplier = Supplier(planner=planner, **data)
        supplier.save()

        logger.info(f"Fornecedor criado com sucesso: uuid={supplier.uuid}")
        return supplier

    @staticmethod
    @transaction.atomic
    def update(instance: Supplier, data: dict[str, Any]) -> Supplier:
        """
        Atualiza uma instância de fornecedor.
        """
        logger.info(f"Atualizando Fornecedor uuid={instance.uuid}")

        # Proteção: Impedimos o sequestro/mudança de dono via API
        data.pop("planner", None)
        data.pop("planner_id", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Fornecedor uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Supplier) -> None:
        """
        Deleta uma instância de fornecedor.
        """
        logger.info(f"Tentativa de deleção do Fornecedor uuid={instance.uuid}")

        try:
            instance.delete()
            logger.warning(f"Fornecedor uuid={instance.uuid} DESTRUÍDO.")

        except ProtectedError as e:
            logger.error(
                f"Falha de integridade ao deletar Fornecedor uuid={instance.uuid}: "
                f"Possui contratos ativos."
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este fornecedor pois existem contratos "
                "vinculados a ele. Remova ou reatribua os contratos primeiro.",
                code="supplier_protected_error",
            ) from e
