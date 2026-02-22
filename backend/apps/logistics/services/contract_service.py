import logging

from django.db import transaction
from django.db.models import ProtectedError

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.logistics.models import Contract, Supplier
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class ContractService:
    """
    Camada de serviço para gestão de contratos.
    Foco: Orquestração, Multitenancy Segura e Auditoria.
    Validações de integridade do dado (ex: datas inválidas) ficam delegadas ao Model.
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Contract:
        logger.info(f"Iniciando criação de Contrato para planner_id={user.id}")

        # 1. Resolução Segura de Dependências (Suporta Instância ou UUID)
        wedding_input = data.pop("wedding", None)
        supplier_input = data.pop("supplier", None)

        # Resolução do Casamento
        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
                wedding = Wedding.objects.all().for_user(user).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de casamento inválido/negado: {wedding_input}"
                )
                raise BusinessRuleViolation(
                    detail="Casamento não encontrado ou acesso negado.",
                    code="wedding_not_found_or_denied",
                ) from e

        # Resolução do Fornecedor
        if isinstance(supplier_input, Supplier):
            supplier = supplier_input
        else:
            try:
                supplier = (
                    Supplier.objects.all().for_user(user).get(uuid=supplier_input)
                )
            except Supplier.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de fornecedor inválido/negado: {supplier_input}"
                )
                raise BusinessRuleViolation(
                    detail="Fornecedor não encontrado ou acesso negado.",
                    code="supplier_not_found_or_denied",
                ) from e

        # 2. Instanciação em Memória
        contract = Contract(planner=user, wedding=wedding, supplier=supplier, **data)

        # 3. Validação Estrita (O Model aplica as suas regras, incluindo checagem de
        # datas)
        contract.full_clean()
        contract.save()

        logger.info(f"Contrato criado com sucesso: uuid={contract.uuid}")
        return contract

    @staticmethod
    @transaction.atomic
    def update(instance: Contract, user, data: dict) -> Contract:
        logger.info(
            f"Atualizando Contrato uuid={instance.uuid} por planner_id={user.id}"
        )

        # Proteção contra sequestro de propriedade
        data.pop("wedding", None)
        data.pop("planner", None)

        # Troca de Fornecedor (com validação multitenant)
        supplier_input = data.pop("supplier", None)
        if supplier_input:
            if isinstance(supplier_input, Supplier):
                instance.supplier = supplier_input
            else:
                try:
                    instance.supplier = (
                        Supplier.objects.all().for_user(user).get(uuid=supplier_input)
                    )
                except Supplier.DoesNotExist as e:
                    raise BusinessRuleViolation(
                        detail="Fornecedor inválido ou acesso negado.",
                        code="supplier_not_found_or_denied",
                    ) from e

        # Atualização dinâmica de campos
        for field, value in data.items():
            if field == "pdf_file" and value is None:
                continue
            setattr(instance, field, value)

        # A regra de 'expiration_date < signed_date' NÃO está mais aqui.
        # Foi enviada para Contract.clean() onde pertence.

        instance.full_clean()
        instance.save()

        logger.info(f"Contrato uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Contract) -> None:
        logger.info(
            f"Tentativa de deleção do Contrato uuid={instance.uuid} por "
            f"planner_id={user.id}"
        )

        # Desvinculação de itens logísticos órfãos
        instance.item_records.update(contract=None)

        try:
            instance.delete()
            logger.warning(
                f"Contrato uuid={instance.uuid} DESTRUÍDO por planner_id={user.id}"
            )

        except ProtectedError as e:
            # Essencial: Se o contrato tem Parcelas Financeiras (Installments)
            # pendentes/pagas, o banco de dados NÃO VAI deixar apagar. O Service
            # intercepta e avisa o Frontend com classe.
            logger.error(
                f"Falha de integridade ao deletar contrato uuid={instance.uuid}"
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este contrato pois existem registros "
                "financeiros (parcelas) vinculados a ele. Apague as parcelas primeiro.",
                code="contract_protected_error",
            ) from e
