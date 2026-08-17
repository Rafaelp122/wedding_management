import logging

from django.db import transaction

from apps.core.tenant import validate_tenant_ownership
from apps.logistics.models import Supplier
from apps.logistics.schemas import SupplierIn, SupplierPatchIn
from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class SupplierService:
    """
    Camada de serviço para gestão de fornecedores.
    Centraliza a lógica de catálogo transversal à Company (RF09).
    Garante auditoria, validação estrita via Model e tratamento de integridade
    referencial para operações de escrita.
    """

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: SupplierIn) -> Supplier:
        """
        Cria um novo fornecedor para o tenant.

        Aplica as validações do modelo ao salvar.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação do fornecedor.

        Returns:
            A instância do Supplier criada e salva.
        """
        logger.info(f"Iniciando criação de Fornecedor para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        supplier = Supplier(company=company, **data)

        # Validação Estrita no Model
        supplier.save()

        logger.info(f"Fornecedor criado com sucesso: uuid={supplier.uuid}")
        return supplier

    @staticmethod
    @transaction.atomic
    def update(
        company: Company, instance: Supplier, payload: SupplierPatchIn
    ) -> Supplier:
        """
        Atualiza os dados de um fornecedor existente.

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
            f"Atualizando Fornecedor uuid={instance.uuid} por company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Fornecedor uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Supplier) -> None:
        """
        Remove um fornecedor do banco de dados.

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
            f"Tentativa de deleção do Fornecedor uuid={instance.uuid} pela "
            f"company_id={company.id}"
        )

        instance.delete()
        logger.warning(
            f"Fornecedor uuid={instance.uuid} DESTRUÍDO pela company_id={company.id}"
        )
