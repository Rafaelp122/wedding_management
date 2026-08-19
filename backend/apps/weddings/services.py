from __future__ import annotations

import logging
from datetime import datetime, time, timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.tenant import validate_tenant_ownership
from apps.scheduler.schemas import EventIn
from apps.tenants.models import Company

from .models import Wedding
from .schemas import (
    WeddingIn,
    WeddingPatchIn,
)


logger = logging.getLogger(__name__)


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de mutação de casamentos.

    Responsável pela criação, atualização e deleção de instâncias de Wedding,
    além de aplicação automática de templates de cronograma.
    """

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: WeddingIn) -> Wedding:
        """
        Cria um novo casamento e opcionalmente aplica um template de cronograma.

        Realiza a persistência do casamento após validar os dados de entrada
        com o método full_clean(). Se especificado no payload, agenda
        automaticamente os eventos de template configurados.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação do casamento.

        Returns:
            A instância de Wedding criada e salva no banco de dados.

        Raises:
            BusinessRuleViolation: Se houver erro de validação nos dados fornecidos.
        """
        logger.info(f"Criando casamento para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        valid_fields = {f.name for f in Wedding._meta.concrete_fields}
        model_data = {k: v for k, v in data.items() if k in valid_fields}

        # Instanciação e Validação do Casamento
        wedding = Wedding(company=company, **model_data)
        try:
            wedding.save()
        except DjangoValidationError as e:
            logger.warning(
                f"Falha de validação ao criar casamento para company_id={company.id}: "
                f"{e}"
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        # ── Template de Cronograma ────────────────────────────────────────
        template_name = data.get("template")
        if template_name is not None:
            logger.info(
                f"Aplicando template '{template_name}' ao casamento uuid={wedding.uuid}"
            )
            _apply_template_events(company, wedding, template_name)

        logger.info(f"Casamento criado com sucesso: uuid={wedding.uuid}")
        return wedding

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Wedding, payload: WeddingPatchIn) -> Wedding:
        """
        Atualiza dados de um casamento existente com base no payload fornecido.

        Garante isolamento de tenant antes de atualizar e executa validações
        com full_clean() antes de persistir as modificações.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância atual de Wedding a ser atualizada.
            payload: Campos modificados a serem aplicados no casamento.

        Returns:
            A instância do casamento atualizada e salva.

        Raises:
            BusinessRuleViolation: Se a atualização violar regras de negócio ou de
                validação do modelo.
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

        valid_fields = {f.name for f in Wedding._meta.concrete_fields}
        for field, value in data.items():
            if field in valid_fields:
                setattr(instance, field, value)

        # Validação estrita
        try:
            instance.save()
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

        logger.info(f"Casamento uuid={instance.uuid} atualizado.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Wedding) -> None:
        """
        Deleta um casamento existente validando a propriedade de tenant.

        Previne a deleção caso existam contratos ou despesas protegidos
        por chaves estrangeiras vinculadas.

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
            f"Tentativa de deleção do casamento uuid={instance.uuid} pela "
            f"company_id={company.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Casamento uuid={instance.uuid} e dependências removidos pela "
                f"company_id={company.id}"
            )

        except ProtectedError as e:
            logger.exception(
                f"Falha de integridade: Casamento uuid={instance.uuid} protegido por "
                f"contratos/despesas."
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este casamento pois existem contratos ou "
                "despesas vinculadas a ele.",
                code="wedding_protected_error",
            ) from e


@transaction.atomic
def _apply_template_events(
    company: Company, wedding: Wedding, template_name: str
) -> None:
    """
    Aplica um template de cronograma criando eventos para o casamento.

    Calcula a data de início de cada evento usando a quantidade de dias
    especificada como offset relativo à data do casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding: O casamento a receber os eventos do template.
        template_name: O identificador/nome do template a ser aplicado.
    """
    from django.utils import timezone

    from apps.scheduler.services import EventService
    from apps.scheduler.services.templates import get_template_events

    template_events = get_template_events(template_name)

    for event_data in template_events:
        offset_days = int(event_data["offset_days"])
        naive_start = datetime.combine(
            wedding.date - timedelta(days=offset_days),
            time(hour=9, minute=0),
        )
        event_start = timezone.make_aware(naive_start)

        EventService.create(
            company,
            EventIn(
                wedding=wedding.uuid,
                title=event_data["title"],
                event_type=event_data["event_type"],
                start_time=event_start,
                location="",
                description="",
            ),
            _allow_historical_start=True,
        )
