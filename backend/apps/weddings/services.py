from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError

from apps.clients.interfaces import (
    get_client_for_tenant,
    get_or_create_client_for_proposal,
)
from apps.contracts.interfaces import (
    get_planner_contract_for_wedding,
    is_planner_contract_signed,
    save_planner_contract_for_wedding,
    sign_planner_contract_for_wedding,
)
from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.core.tenant import validate_tenant_ownership
from apps.finances.interfaces import (
    create_expense_from_planner_contract,
    freeze_budget_baseline_for_wedding,
)
from apps.tenants.models import Company
from apps.weddings.models import Wedding, WeddingClient
from apps.weddings.schemas import (
    PlannerContractIn,
    WeddingIn,
    WeddingPatchIn,
    WeddingProposalIn,
)


logger = logging.getLogger(__name__)


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de mutação de casamentos.

    Responsável pela criação, atualização, propostas comerciais, contratos de
    honorários da assessoria e conversão de propostas para planejamento ativo.

    Regras de Negócio e SSOT:
    - BR-W01 a BR-W06 (Ciclo de Vida do Casamento):
      docs/architecture/business-rules/weddings/wedding-status-lifecycle.md
    - BR-W07 (Templates Canônicos de Cronograma):
      docs/architecture/business-rules/weddings/wedding-schedule-templates.md
    - RFC-001 (Ciclo Comercial & Domínio Weddings):
      docs/architecture/rfc/001-macro-architecture-and-domain-redesign.md
    """

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: WeddingIn) -> Wedding:
        """
        Cria um novo casamento diretamente em andamento e opcionalmente aplica template.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação do casamento.

        Returns:
            A instância de Wedding criada e persistida.

        Raises:
            BusinessRuleViolation: Se houver erro de validação nos dados fornecidos.
        """
        logger.info(f"Criando casamento para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)
        template_name = data.get("template")

        wedding = Wedding(
            company=company,
            groom_name=payload.groom_name,
            bride_name=payload.bride_name,
            date=payload.date,
            location=payload.location,
            expected_guests=payload.expected_guests,
            template=template_name,
            client_name=payload.client_name,
            client_cpf=payload.client_cpf,
            client_email=payload.client_email,
            client_phone=payload.client_phone,
            client_role=payload.client_role,
            days_before_in_progress=payload.days_before_in_progress,
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        try:
            wedding.save()
        except DjangoValidationError as e:
            logger.warning(
                f"Falha de validação ao criar casamento para company_id={company.id}: {e}"
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        if template_name is not None:
            logger.info(
                f"Aplicando template '{template_name}' ao casamento uuid={wedding.uuid}"
            )
            _apply_template_events(company, wedding, template_name)

        logger.info(f"Casamento criado com sucesso: uuid={wedding.uuid}")
        return wedding

    @staticmethod
    @transaction.atomic
    def create_proposal(company: Company, payload: WeddingProposalIn) -> Wedding:
        """
        Cria uma proposta comercial de casamento no status preliminar PROPOSAL.

        Permite à assessoria simular dados, orçamentos e emitir propostas antes
        da assinatura do contrato oficial de prestação de serviços.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada da proposta comercial.

        Returns:
            A instância de Wedding criada com status PROPOSAL.

        Raises:
            BusinessRuleViolation: Se houver erro de validação cadastral.
        """
        logger.info(
            f"Criando proposta comercial de casamento para company_id={company.id}"
        )

        wedding = Wedding(
            company=company,
            groom_name=payload.groom_name,
            bride_name=payload.bride_name,
            date=payload.date,
            location=payload.location,
            expected_guests=payload.expected_guests,
            template=payload.template,
            client_name=payload.client_name,
            client_cpf=payload.client_cpf,
            client_email=payload.client_email,
            client_phone=payload.client_phone,
            client_role=payload.client_role,
            days_before_in_progress=payload.days_before_in_progress,
            status=Wedding.StatusChoices.PROPOSAL,
        )
        try:
            wedding.save()
        except DjangoValidationError as e:
            logger.warning(
                f"Falha de validação ao criar proposta para company_id={company.id}: {e}"
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        if payload.client_name:
            client = get_or_create_client_for_proposal(
                company=company,
                name=payload.client_name,
                cpf=payload.client_cpf or "",
                email=payload.client_email or "",
                phone=payload.client_phone or "",
            )
            WeddingClient.objects.create(
                company=company,
                wedding=wedding,
                client=client,
                role=WeddingClient.RoleChoices.FINANCIAL_PAYER,
                is_primary_signatory=True,
            )

        logger.info(f"Proposta de casamento criada com sucesso: uuid={wedding.uuid}")
        return wedding

    create_wedding_proposal = create_proposal

    @staticmethod
    @transaction.atomic
    def save_planner_contract(
        company: Company,
        wedding: Wedding,
        payload: PlannerContractIn,
    ) -> tuple[Any, bool]:
        """
        Cria ou atualiza o contrato de honorários da assessoria cerimonial.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding: Instância do casamento associado.
            payload: Dados do contrato de honorários.

        Returns:
            Tupla contendo a instância de Contract e um booleano
            indicando se foi criado (True) ou atualizado (False).

        Raises:
            BusinessRuleViolation: Se os dados violarem as regras do contrato.
        """
        validate_tenant_ownership(
            company,
            wedding,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )

        data = payload.model_dump(exclude_unset=True)
        return save_planner_contract_for_wedding(
            company=company,
            wedding=wedding,
            service_tier=data.get("service_tier"),
            total_amount=data.get("effective_amount"),
            installments_count=data.get("installments_count"),
            signed_date=data.get("signed_date"),
            status=data.get("status"),
        )

    @staticmethod
    @transaction.atomic
    def convert_wedding_to_planning(
        company: Company,
        wedding_id: UUID | str,
        category_id: UUID | str | None = None,
    ) -> Wedding:
        """
        Converte uma proposta de casamento para a fase ativa de planejamento (PLANNING).

        Executa as seguintes etapas atomicamente:
        1. Valida a existência do casamento sob o tenant;
        2. Valida e garante a assinatura do contrato de honorários via interface de contratos;
        3. Transiciona a máquina de estados do casamento para PLANNING;
        4. Congela a linha de base original do orçamento mestre (freeze_baseline);
        5. Invoca o módulo de Finanças para lançar a despesa de honorários e parcelas;
        6. Aplica o template de cronograma, se configurado;
        7. Enfileira a tarefa assíncrona pós-commit on_wedding_activated_task.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_id: Identificador UUID ou PK do casamento.
            category_id: Categoria orçamentária opcional para os honorários.

        Returns:
            A instância de Wedding ativada.

        Raises:
            BusinessRuleViolation: Se o contrato de assessoria estiver ausente
                ou se a conversão violar regras de negócio.
        """
        wedding = get_object_or_404_for_tenant(
            Wedding,
            company,
            wedding_id,
            select_related=["company"],
            code="wedding_not_found_or_denied",
        )

        contract = get_planner_contract_for_wedding(company=company, wedding=wedding)
        if not contract:
            raise BusinessRuleViolation(
                detail="O casamento deve possuir um contrato de assessoria para iniciar o planejamento.",
                code="planner_contract_required",
            )

        if not is_planner_contract_signed(company=company, wedding=wedding):
            contract = sign_planner_contract_for_wedding(
                company=company, wedding=wedding
            )

        wedding.convert_to_planning()
        try:
            wedding.save(update_fields=["status", "updated_at"])
        except DjangoValidationError as e:
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        # Congela a linha de base original do orçamento mestre (Pacote 3)
        freeze_budget_baseline_for_wedding(company=company, wedding=wedding)

        # Integração síncrona com o Bounded Context de Finanças (ADR-031)
        create_expense_from_planner_contract(
            company=company,
            wedding=wedding,
            planner_contract=contract,
            category_id=category_id,
        )

        # Aplicação de template de cronograma se configurado
        if wedding.template:
            _apply_template_events(company, wedding, wedding.template)

        # Despacho reativo e assíncrono pós-commit (RFC-001)
        from apps.weddings.tasks import on_wedding_activated_task

        transaction.on_commit(
            lambda: on_wedding_activated_task.enqueue(
                company.id, str(wedding.uuid), wedding.template
            )
        )

        logger.info(
            f"Casamento uuid={wedding.uuid} convertido para planejamento com sucesso."
        )
        return wedding

    @staticmethod
    def _handle_status_update(
        company: Company, instance: Wedding, status_input: str | None
    ) -> bool:
        if status_input is None or status_input == instance.status:
            return False
        instance.transition_to(status_input)
        if instance.status == Wedding.StatusChoices.CANCELED:
            from apps.weddings.tasks import on_wedding_canceled_task

            transaction.on_commit(
                lambda: on_wedding_canceled_task.enqueue(company.id, str(instance.uuid))
            )
        return True

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Wedding, payload: WeddingPatchIn) -> Wedding:
        """
        Atualiza dados de um casamento existente delegando mutações ao modelo.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância atual de Wedding a ser atualizada.
            payload: Campos modificados a serem aplicados no casamento.

        Returns:
            A instância do casamento atualizada e salva.

        Raises:
            BusinessRuleViolation: Se a atualização violar regras de negócio.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )
        logger.info(
            f"Atualizando casamento uuid={instance.uuid} pela company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)
        updated_fields: set[str] = set()

        if WeddingService._handle_status_update(
            company, instance, data.pop("status", None)
        ):
            updated_fields.add("status")

        new_date = data.pop("date", None)
        if new_date is not None and new_date != instance.date:
            instance.reschedule(new_date)
            updated_fields.add("date")

        old_guests = instance.expected_guests or 0
        new_guests = data.get("expected_guests")

        detail_kwargs: dict[str, Any] = {}
        for field in (
            "groom_name",
            "bride_name",
            "location",
            "expected_guests",
            "client_name",
            "client_cpf",
            "client_email",
            "client_phone",
            "client_role",
            "days_before_in_progress",
        ):
            if field in data:
                detail_kwargs[field] = data[field]
                updated_fields.add(field)

        if detail_kwargs:
            instance.update_details(**detail_kwargs)

        if updated_fields:
            updated_fields.add("updated_at")
            try:
                instance.save(update_fields=list(updated_fields))
            except DjangoValidationError as e:
                logger.warning(
                    f"Falha de validação ao atualizar casamento uuid={instance.uuid} "
                    f"pela company_id={company.id}: {e}"
                )
                detail = "; ".join(e.messages) if e.messages else str(e)
                raise BusinessRuleViolation(
                    detail=detail,
                    code="wedding_validation_error",
                ) from e

        if new_guests is not None and new_guests != old_guests:
            from apps.contracts.interfaces import enqueue_guest_count_evaluation

            enqueue_guest_count_evaluation(
                company_id=company.id,
                wedding_uuid=instance.uuid,
                old_count=old_guests,
                new_count=new_guests,
            )

        logger.info(f"Casamento uuid={instance.uuid} atualizado.")
        return instance

    @staticmethod
    @transaction.atomic
    def complete(company: Company, instance: Wedding) -> Wedding:
        """
        Caso de uso: Conclui um casamento existente delegando a regra para a entidade.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância de Wedding a ser concluída.

        Returns:
            A instância de Wedding concluída e persistida.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )
        instance.complete()
        try:
            instance.save(update_fields=["status", "updated_at"])
        except DjangoValidationError as e:
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        logger.info(f"Casamento uuid={instance.uuid} concluído com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def cancel(company: Company, instance: Wedding) -> Wedding:
        """
        Caso de uso: Cancela um casamento existente delegando a regra para a entidade.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância de Wedding a ser cancelada.

        Returns:
            A instância de Wedding cancelada e persistida.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )
        instance.cancel()
        try:
            instance.save(update_fields=["status", "updated_at"])
        except DjangoValidationError as e:
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        from apps.weddings.tasks import on_wedding_canceled_task

        transaction.on_commit(
            lambda: on_wedding_canceled_task.enqueue(company.id, str(instance.uuid))
        )

        logger.info(f"Casamento uuid={instance.uuid} cancelado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def reopen(*, company: Company, instance: Wedding) -> Wedding:
        """
        Reabre um casamento previamente cancelado voltando para EM ANDAMENTO.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância de Wedding a ser reaberta.

        Returns:
            A instância de Wedding reaberta e persistida.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )
        instance.reopen()
        try:
            instance.save(update_fields=["status", "updated_at"])
        except DjangoValidationError as e:
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        logger.info(f"Casamento uuid={instance.uuid} reaberto com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Wedding) -> None:
        """
        Deleta um casamento existente validando a propriedade de tenant.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância de Wedding a ser deletada.

        Raises:
            DomainIntegrityError: Se houver violação de integridade ou se
                o casamento possuir relacionamentos protegidos.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )
        logger.info(
            f"Tentativa de deleção do casamento uuid={instance.uuid} pela company_id={company.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Casamento uuid={instance.uuid} e dependências removidos pela company_id={company.id}"
            )
        except ProtectedError as e:
            logger.exception(
                f"Falha de integridade: Casamento uuid={instance.uuid} protegido por contratos/despesas."
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este casamento pois existem contratos ou "
                "despesas vinculadas a ele.",
                code="wedding_protected_error",
            ) from e

    @staticmethod
    def add_participant(
        company: Company,
        wedding_id: UUID | str,
        client_id: UUID | str,
        role: str,
        is_primary_signatory: bool = False,
        notes: str = "",
    ) -> WeddingClient:
        """
        Adiciona um participante ao casamento delegando para a função pública de domínio.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_id: Identificador único do casamento.
            client_id: Identificador único do cliente.
            role: Papel do participante no evento.
            is_primary_signatory: Se o participante deve assinar o contrato.
            notes: Observações cadastrais sobre a participação.

        Returns:
            A instância de WeddingClient criada e vinculada.
        """
        return add_wedding_participant(
            company=company,
            wedding_id=wedding_id,
            client_id=client_id,
            role=role,
            is_primary_signatory=is_primary_signatory,
            notes=notes,
        )

    @staticmethod
    def remove_participant(
        company: Company,
        wedding_id: UUID | str,
        participant_id: UUID | str,
    ) -> None:
        """
        Remove um participante do casamento delegando para a função pública de domínio.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_id: Identificador único do casamento.
            participant_id: Identificador único do participante.

        Returns:
            None.
        """
        remove_wedding_participant(
            company=company,
            wedding_id=wedding_id,
            participant_id=participant_id,
        )


@transaction.atomic
def add_wedding_participant(
    company: Company,
    wedding_id: UUID | str,
    client_id: UUID | str,
    role: str,
    is_primary_signatory: bool = False,
    notes: str = "",
) -> WeddingClient:
    """
    Adiciona um cliente como participante vinculado a um casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador único do casamento.
        client_id: Identificador único do cliente a ser vinculado.
        role: Papel do participante no casamento (ex: BRIDE, GROOM, FINANCIAL_PAYER).
        is_primary_signatory: Indica se o participante assina o contrato.
        notes: Observações cadastrais sobre a participação.

    Returns:
        A instância de WeddingClient criada e persistida.

    Raises:
        ObjectNotFoundError: Se o casamento ou cliente não pertencerem ao tenant.
        BusinessRuleViolation: Se o participante já estiver com o mesmo papel.
    """
    wedding = get_object_or_404_for_tenant(Wedding, company, uuid=wedding_id)
    client = get_client_for_tenant(company=company, client_id=client_id)

    if WeddingClient.objects.filter(
        company=company, wedding=wedding, client=client, role=role
    ).exists():
        raise BusinessRuleViolation(
            detail=f"O cliente já está cadastrado como '{role}' neste casamento.",
            code="wedding_participant_already_exists",
        )

    participant = WeddingClient(
        company=company,
        wedding=wedding,
        client=client,
        role=role,
        is_primary_signatory=is_primary_signatory,
        notes=notes,
    )
    try:
        participant.save()
    except DjangoValidationError as exc:
        detail = "; ".join(exc.messages) if exc.messages else str(exc)
        raise BusinessRuleViolation(
            detail=detail,
            code="wedding_participant_validation_error",
        ) from exc

    return participant


@transaction.atomic
def remove_wedding_participant(
    company: Company,
    wedding_id: UUID | str,
    participant_id: UUID | str,
) -> None:
    """
    Remove um participante vinculado a um casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador único do casamento.
        participant_id: Identificador único do participante (WeddingClient).

    Returns:
        None.

    Raises:
        ObjectNotFoundError: Se o casamento ou participante não existirem no tenant.
        BusinessRuleViolation: Se o participante não pertencer ao casamento informado.
    """
    wedding = get_object_or_404_for_tenant(Wedding, company, uuid=wedding_id)
    participant = get_object_or_404_for_tenant(
        WeddingClient, company, uuid=participant_id
    )

    if participant.wedding_id != wedding.id:
        raise BusinessRuleViolation(
            detail="O participante não pertence ao casamento especificado.",
            code="wedding_participant_mismatch",
        )

    participant.delete()


def create_wedding_proposal(company: Company, payload: WeddingProposalIn) -> Wedding:
    """
    Função pública de fachada para criação de proposta de casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        payload: Dados cadastrais da proposta de casamento.

    Returns:
        A instância de Wedding persistida no status PROPOSAL.
    """
    return WeddingService.create_proposal(company=company, payload=payload)


def convert_wedding_to_planning(
    company: Company,
    wedding_id: UUID | str,
    category_id: UUID | str | None = None,
) -> Wedding:
    """
    Função pública de fachada para ativação/conversão de casamento para planejamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador único do casamento a converter.
        category_id: Categoria orçamentária opcional para os honorários.

    Returns:
        A instância de Wedding ativada no status IN_PROGRESS.
    """
    return WeddingService.convert_wedding_to_planning(
        company=company, wedding_id=wedding_id, category_id=category_id
    )


@transaction.atomic
def _apply_template_events(
    company: Company, wedding: Wedding, template_name: str
) -> None:
    """
    Aplica um template de cronograma criando eventos para o casamento.
    Delega para a fachada pública de interfaces do módulo scheduler.
    """
    from apps.scheduler.interfaces import apply_wedding_schedule_template

    apply_wedding_schedule_template(
        company=company,
        wedding=wedding,
        template_name=template_name,
    )
