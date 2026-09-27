"""Serviços de escrita do domínio de Fornecedores (apps.suppliers)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import transaction

from apps.core.tenant import validate_tenant_ownership
from apps.suppliers.models import Supplier


if TYPE_CHECKING:
    from apps.suppliers.schemas import SupplierIn, SupplierPatchIn
    from apps.tenants.models import Company

logger = logging.getLogger(__name__)


class SupplierService:
    """Camada de serviço para gestão de fornecedores.

    Centraliza a lógica de catálogo transversal à Company (RF09).
    Garante auditoria, validação estrita via Model e tratamento de integridade
    referencial para operações de escrita.
    """

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: SupplierIn) -> Supplier:
        """Cria um novo fornecedor para o tenant.

        Aplica as validações do modelo ao salvar.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação do fornecedor.

        Returns:
            A instância do Supplier criada e salva.
        """
        logger.info("Iniciando criação de Fornecedor para company_id=%s", company.id)

        data = payload.model_dump(exclude_unset=True)

        supplier = Supplier(company=company, **data)

        # Validação Estrita no Model (BaseModel.full_clean no save)
        supplier.save()

        logger.info("Fornecedor criado com sucesso: uuid=%s", supplier.uuid)
        return supplier

    @staticmethod
    @transaction.atomic
    def update(
        company: Company, instance: Supplier, payload: SupplierPatchIn
    ) -> Supplier:
        """Atualiza os dados de um fornecedor existente.

        Valida a propriedade do tenant antes de aplicar e salvar as alterações.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Supplier a ser atualizada.
            payload: Dados parciais para atualização do fornecedor.

        Returns:
            A instância atualizada do Supplier.

        Raises:
            ObjectNotFoundError: Se o fornecedor não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Fornecedor não encontrado ou acesso negado.",
            code="supplier_not_found_or_denied",
        )
        logger.info(
            "Atualizando Fornecedor uuid=%s por company_id=%s",
            instance.uuid,
            company.id,
        )

        updated_fields: set[str] = set()
        data = payload.model_dump(exclude_unset=True)

        if "is_active" in data:
            is_active = data.pop("is_active")
            if is_active:
                instance.activate()
            else:
                instance.deactivate()
            updated_fields.add("is_active")

        for field, value in data.items():
            setattr(instance, field, value)
            updated_fields.add(field)

        if updated_fields:
            updated_fields.add("updated_at")
            instance.save(update_fields=list(updated_fields))

        logger.info("Fornecedor uuid=%s atualizado com sucesso.", instance.uuid)
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Supplier) -> None:
        """Remove um fornecedor do banco de dados.

        Valida a propriedade do tenant antes da exclusão.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Supplier a ser removida.

        Raises:
            ObjectNotFoundError: Se o fornecedor não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Fornecedor não encontrado ou acesso negado.",
            code="supplier_not_found_or_denied",
        )
        logger.info(
            "Tentativa de deleção do Fornecedor uuid=%s pela company_id=%s",
            instance.uuid,
            company.id,
        )

        instance.delete()
        logger.warning(
            "Fornecedor uuid=%s DESTRUÍDO pela company_id=%s",
            instance.uuid,
            company.id,
        )
