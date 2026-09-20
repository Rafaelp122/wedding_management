"""Schemas Pydantic/Ninja para a entidade de Despesa (Expense)."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


if TYPE_CHECKING:
    from apps.finances.models.expense import Expense


class ExpenseIn(Schema):
    """Schema de entrada para criação de despesa."""

    model_config = ConfigDict(str_strip_whitespace=True)

    category: UUID4
    contract: UUID4 | None = None
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=1000)
    estimated_amount: Decimal = Field(ge=0)
    actual_amount: Decimal = Field(ge=0)
    num_installments: int | None = Field(default=None, gt=0)
    first_due_date: date | None = None


class ExpensePatchIn(Schema):
    """Schema de entrada para atualização parcial de despesa."""

    model_config = ConfigDict(str_strip_whitespace=True)

    contract: UUID4 | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str = Field(default="", max_length=1000)
    estimated_amount: Decimal | None = Field(default=None, ge=0)
    actual_amount: Decimal | None = Field(default=None, ge=0)


class ExpenseRenegotiateIn(Schema):
    """Schema de entrada para renegociação e redistribuição de parcelas."""

    model_config = ConfigDict(str_strip_whitespace=True)

    num_installments: int = Field(gt=0)
    first_due_date: date | None = None


class ExpenseFromDocumentOut(Schema):
    """Schema de saída com dados extraídos de documento/contrato."""

    name: str
    description: str = ""
    contract: UUID4
    actual_amount: Decimal
    category_uuid: UUID4 | None = None
    num_installments: int | None = None
    first_due_date: date | None = None


class ContractLookupOut(Schema):
    """Schema de saída para listagem simplificada de contratos em dropdowns/lookups."""

    uuid: UUID4
    name: str
    status: str
    total_amount: Decimal


class ExpenseOut(Schema):
    """Schema de saída para exibição de despesa (CQRS puro sem queries ORM)."""

    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    category: UUID4 = Field(alias="category.uuid")
    contract: UUID4 | None = None

    name: str
    description: str = ""
    estimated_amount: Decimal
    actual_amount: Decimal
    category_name: str = ""
    contract_description: str | None = None
    status: str = "PENDING"
    installments_count: int = 0
    paid_installments_count: int = 0
    total_paid: Decimal = Decimal("0.00")
    total_pending: Decimal = Decimal("0.00")
    payment_progress_percent: int = 0

    @staticmethod
    def resolve_payment_progress_percent(obj: Any) -> int:
        """Resolve o percentual de pagamento a partir da propriedade de domínio."""
        val = getattr(obj, "payment_progress_percent", None)
        if val is not None:
            return int(val)
        actual = getattr(obj, "actual_amount", None)
        total_paid = getattr(obj, "total_paid", None)
        if actual and actual > Decimal("0.00") and total_paid:
            return int((total_paid / actual) * 100)
        return 0

    @staticmethod
    def resolve_wedding(obj: "Expense") -> UUID4:
        """Resolve o UUID do casamento."""
        return obj.wedding.uuid

    @staticmethod
    def resolve_category(obj: "Expense") -> UUID4:
        """Resolve o UUID da categoria."""
        return obj.category.uuid

    @staticmethod
    def resolve_contract(obj: "Expense") -> UUID4 | None:
        """Resolve o UUID do contrato se já estiver em memória, sem query ad-hoc."""
        if obj.contract_id:
            if hasattr(obj, "_state") and "contract" in obj._state.fields_cache:
                contract = obj._state.fields_cache["contract"]
                return contract.uuid if contract else None
        return None

    @staticmethod
    def resolve_category_name(obj: "Expense") -> str:
        """Resolve o nome da categoria usando atributos em memória."""
        val = getattr(obj, "category_name", None)
        if val is not None:
            return str(val)
        if hasattr(obj, "_state") and "category" in obj._state.fields_cache:
            cat = obj._state.fields_cache["category"]
            return cat.name if cat else ""
        try:
            return obj.category.name
        except Exception:
            return ""

    @staticmethod
    def resolve_contract_description(obj: "Expense") -> str | None:
        """Resolve a descrição do contrato usando atributos em memória."""
        val = getattr(obj, "contract_description", None)
        if val is not None:
            return str(val)
        if (
            obj.contract_id
            and hasattr(obj, "_state")
            and "contract" in obj._state.fields_cache
        ):
            contract = obj._state.fields_cache["contract"]
            return contract.description if contract else None
        return None

    @staticmethod
    def resolve_status(obj: Any) -> str:
        """Resolve o status da despesa a partir do domínio ou contagens."""
        status = getattr(obj, "status", None)
        if isinstance(status, str):
            return status

        total = int(getattr(obj, "installments_count", 0) or 0)
        paid = int(getattr(obj, "paid_installments_count", 0) or 0)

        if total == 0:
            return "PENDING"
        if paid >= total:
            return "SETTLED"
        if paid > 0:
            return "PARTIALLY_PAID"
        return "PENDING"

    @staticmethod
    def resolve_installments_count(obj: "Expense") -> int:
        """Retorna o número de parcelas a partir de atributo anotado."""
        return int(getattr(obj, "installments_count", 0) or 0)

    @staticmethod
    def resolve_paid_installments_count(obj: "Expense") -> int:
        """Retorna o número de parcelas pagas a partir de atributo anotado."""
        return int(getattr(obj, "paid_installments_count", 0) or 0)

    @staticmethod
    def resolve_total_paid(obj: "Expense") -> Decimal:
        """Retorna o valor total pago a partir de atributo anotado."""
        return Decimal(str(getattr(obj, "total_paid", "0.00") or "0.00"))

    @staticmethod
    def resolve_total_pending(obj: "Expense") -> Decimal:
        """Retorna o valor total pendente a partir de atributo anotado."""
        return Decimal(str(getattr(obj, "total_pending", "0.00") or "0.00"))
