import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import (
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.logistics.models import Supplier
from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class SupplierService:
    """
    Camada de serviço para gestão de fornecedores.
    Centraliza a lógica de catálogo transversal à Company (RF09).
    Garante auditoria, validação estrita via Model e tratamento de integridade
    referencial.
    """

    @staticmethod
    def list(company: Company) -> QuerySet[Supplier]:
        return Supplier.objects.for_tenant(company)

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Supplier:
        try:
            return Supplier.objects.for_tenant(company).get(uuid=uuid)
        except Supplier.DoesNotExist as e:
            raise ObjectNotFoundError(detail="Fornecedor não encontrado.") from e

    @staticmethod
    @transaction.atomic
    def create(company: Company, data: dict[str, Any]) -> Supplier:
        logger.info(f"Iniciando criação de Fornecedor para company_id={company.id}")

        # 1. Instanciação em Memória
        supplier = Supplier(company=company, **data)

        # 2. Validação Estrita no Model
        supplier.save()

        logger.info(f"Fornecedor criado com sucesso: uuid={supplier.uuid}")
        return supplier

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Supplier, data: dict[str, Any]) -> Supplier:
        logger.info(
            f"Atualizando Fornecedor uuid={instance.uuid} por company_id={company.id}"
        )

        # Proteção: Impedimos o sequestro/mudança de dono via API
        data.pop("company", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Fornecedor uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Supplier) -> None:
        logger.info(
            f"Tentativa de deleção do Fornecedor uuid={instance.uuid} pela "
            f"company_id={company.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Fornecedor uuid={instance.uuid} DESTRUÍDO pela "
                f"company_id={company.id}"
            )

        except ProtectedError as e:
            # Captura a trava do banco de dados (relacionamento com Contract) e formata
            # para o Frontend
            logger.error(
                f"Falha de integridade ao deletar Fornecedor uuid={instance.uuid}: "
                f"Possui contratos ativos."
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este fornecedor pois existem contratos "
                "vinculados a ele. Remova ou reatribua os contratos primeiro.",
                code="supplier_protected_error",
            ) from e
