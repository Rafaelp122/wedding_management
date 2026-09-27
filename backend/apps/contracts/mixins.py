import datetime as dt
from typing import Any

from django.db import models
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation


class SignableDocumentMixin(models.Model):
    """
    Mixin para entidades que representam documentos assináveis.

    Fornece lógica comum de ciclo de vida e gerenciamento de arquivos
    para contratos, termos aditivos e outros documentos formais.
    """

    status: str
    signed_date: dt.date | None

    class Meta:
        abstract = True

    def can_transition_to(self, target_status: str | Any) -> bool:
        """Verifica se a transição para o status informado é válida.

        Args:
            target_status: Status de destino pretendido.

        Returns:
            True se a transição for permitida, False caso contrário.
        """
        target = str(target_status)
        if self.status == target:
            return True

        # O modelo deve definir PLANNER_ALLOWED_TRANSITIONS ou ALLOWED_TRANSITIONS
        if (
            hasattr(self, "contract_type")
            and hasattr(self, "ContractTypeChoices")
            and self.contract_type == getattr(self.ContractTypeChoices, "PLANNER", None)
        ):
            allowed_dict = getattr(self, "PLANNER_ALLOWED_TRANSITIONS", {})
        else:
            allowed_dict = getattr(self, "ALLOWED_TRANSITIONS", {})

        allowed = allowed_dict.get(self.status, [])
        return target in allowed

    def transition_to(self, target_status: str | Any) -> None:
        """Executa a transição de status validando as regras do autômato de estados.

        Args:
            target_status: Status de destino para transição.

        Raises:
            BusinessRuleViolation: Se a transição for negada pelas regras de negócio.
        """
        target = str(target_status)
        if self.status == target:
            return

        status_choices = getattr(self, "StatusChoices", None)
        signed_status = getattr(status_choices, "SIGNED", "SIGNED")
        canceled_status = getattr(status_choices, "CANCELED", "CANCELED")

        if (
            hasattr(self, "contract_type")
            and hasattr(self, "ContractTypeChoices")
            and self.contract_type == getattr(self.ContractTypeChoices, "PLANNER", None)
            and target == signed_status
            and self.status == canceled_status
        ):
            raise BusinessRuleViolation(
                detail="Não é possível assinar um contrato cancelado.",
                code="planner_contract_already_canceled",
            )

        if not self.can_transition_to(target):
            raise BusinessRuleViolation(
                detail=f"Não é permitido transitar de '{self.status}' para '{target}'.",
                code="invalid_status_transition",
            )

        self.status = target

    def sign(self, signed_date: dt.date | None = None, pdf_file: Any = None) -> None:
        """Formaliza a assinatura do documento.

        Args:
            signed_date: Data formal da assinatura do instrumento.
            pdf_file: Arquivo opcional do documento assinado.
        """
        if signed_date is not None:
            self.signed_date = signed_date
        elif not getattr(self, "signed_date", None):
            self.signed_date = timezone.now().date()

        if pdf_file is not None and hasattr(self, "pdf_file"):
            self.pdf_file = pdf_file

        status_choices = getattr(self, "StatusChoices", None)
        signed_status = getattr(status_choices, "SIGNED", "SIGNED")
        self.transition_to(signed_status)

    def cancel(self) -> None:
        """Cancela o documento formalmente."""
        status_choices = getattr(self, "StatusChoices", None)
        canceled_status = getattr(status_choices, "CANCELED", "CANCELED")
        self.transition_to(canceled_status)

    @property
    def has_file(self) -> bool:
        """Indica se o documento possui arquivo PDF anexado."""
        return bool(getattr(self, "pdf_file", None))

    @property
    def file_name(self) -> str | None:
        """Retorna o nome do arquivo anexado ao documento, se houver."""
        pdf_file = getattr(self, "pdf_file", None)
        if pdf_file and getattr(pdf_file, "name", None):
            return str(pdf_file.name).split("/")[-1]
        return None
