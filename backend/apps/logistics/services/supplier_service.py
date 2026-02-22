import logging

from django.db import transaction
from django.db.models import ProtectedError

from apps.core.exceptions import DomainIntegrityError
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
    @transaction.atomic
    def create(user, data: dict) -> Supplier:
        logger.info(f"Iniciando criação de Fornecedor para planner_id={user.id}")

        # 1. Instanciação em Memória (O Fornecedor é PlannerOwned, transversal)
        supplier = Supplier(planner=user, **data)

        # 2. Validação Estrita no Model (CNPJ único, formatação de telefone, etc.)
        supplier.full_clean()
        supplier.save()

        logger.info(f"Fornecedor criado com sucesso: uuid={supplier.uuid}")
        return supplier

    @staticmethod
    @transaction.atomic
    def update(instance: Supplier, user, data: dict) -> Supplier:
        logger.info(
            f"Atualizando Fornecedor uuid={instance.uuid} por planner_id={user.id}"
        )

        # Proteção: Impedimos o sequestro/mudança de dono via API
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # O full_clean() aqui é vital para re-validar regras de negócio
        # (ex: CNPJ duplicado)
        instance.full_clean()
        instance.save()

        logger.info(f"Fornecedor uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Supplier) -> None:
        logger.info(
            f"Tentativa de deleção do Fornecedor uuid={instance.uuid} por "
            f"planner_id={user.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Fornecedor uuid={instance.uuid} DESTRUÍDO por planner_id={user.id}"
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
