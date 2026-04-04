import logging
from typing import Any
from uuid import UUID

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.core.types import AuthContextUser
from apps.logistics.models import Supplier
from apps.users.models import User


logger = logging.getLogger(__name__)


class SupplierService:
    """
    Camada de serviço para gestão de fornecedores.
    Centraliza a lógica de catálogo transversal ao Planner (RF09).
    Garante auditoria, validação estrita via Model e tratamento de integridade
    referencial.
    """

    @staticmethod
    def _require_user(user: AuthContextUser) -> User:
        if isinstance(user, AnonymousUser):
            raise BusinessRuleViolation(
                detail="Autenticação obrigatória para executar esta operação.",
                code="authentication_required",
            )
        return user

    @staticmethod
    def list(user: AuthContextUser) -> QuerySet[Supplier]:
        return Supplier.objects.for_user(user)

    @staticmethod
    def get(user: AuthContextUser, uuid: UUID | str) -> Supplier:
        from django.shortcuts import get_object_or_404

        return get_object_or_404(Supplier.objects.for_user(user), uuid=uuid)

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Supplier:
        planner = SupplierService._require_user(user)
        logger.info(f"Iniciando criação de Fornecedor para planner_id={planner.id}")

        # 1. Instanciação em Memória (O Fornecedor é PlannerOwned, transversal)
        supplier = Supplier(planner=planner, **data)

        # 2. Validação Estrita no Model (CNPJ único, formatação de telefone, etc.)
        supplier.save()

        logger.info(f"Fornecedor criado com sucesso: uuid={supplier.uuid}")
        return supplier

    @staticmethod
    @transaction.atomic
    def update(
        user: AuthContextUser, instance: Supplier, data: dict[str, Any]
    ) -> Supplier:
        logger.info(
            f"Atualizando Fornecedor uuid={instance.uuid} por planner_id={user.id}"
        )

        # Proteção: Impedimos o sequestro/mudança de dono via API
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # O full_clean() aqui é vital para re-validar regras de negócio
        # (ex: CNPJ duplicado)
        instance.save()

        logger.info(f"Fornecedor uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def partial_update(
        user: AuthContextUser, instance: Supplier, data: dict[str, Any]
    ) -> Supplier:
        """Alias estrutural."""
        return SupplierService.update(user, instance, data)

    @staticmethod
    @transaction.atomic
    def delete(user: AuthContextUser, instance: Supplier) -> None:
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
