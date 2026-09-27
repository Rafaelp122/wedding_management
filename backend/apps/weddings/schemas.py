import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from ninja import Field, Schema
from pydantic import UUID4


if TYPE_CHECKING:
    from apps.weddings.models import Wedding


class WeddingStatusEnum(StrEnum):
    PROPOSAL = "PROPOSAL"
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class PlannerContractServiceTierEnum(StrEnum):
    COMPLETA = "COMPLETA"
    PARCIAL = "PARCIAL"
    FINAL = "FINAL"


class PlannerContractStatusEnum(StrEnum):
    DRAFT = "DRAFT"
    SIGNED = "SIGNED"
    CANCELED = "CANCELED"


class PlannerContractIn(Schema):
    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    service_tier: PlannerContractServiceTierEnum | str = Field(
        default=PlannerContractServiceTierEnum.COMPLETA
    )
    effective_amount: Decimal = Field(..., ge=0)
    installments_count: int = Field(default=1, ge=1)
    signed_date: datetime.date | None = None
    status: PlannerContractStatusEnum | str = Field(
        default=PlannerContractStatusEnum.DRAFT
    )


class PlannerContractOut(Schema):
    uuid: UUID4
    service_tier: str
    effective_amount: Decimal
    installments_count: int
    signed_date: datetime.date | None = None
    pdf_file: str | None = None
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @staticmethod
    def resolve_pdf_file(obj: Any) -> str | None:
        if hasattr(obj, "pdf_file") and obj.pdf_file:
            try:
                return str(obj.pdf_file.url)
            except Exception:
                return str(obj.pdf_file)
        return None


class WeddingIn(Schema):
    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    groom_name: str = Field(..., min_length=1, max_length=100)
    bride_name: str = Field(..., min_length=1, max_length=100)
    date: datetime.date
    location: str = Field(..., min_length=1, max_length=255)
    expected_guests: int | None = Field(default=None, ge=1)
    template: str | None = Field(default=None, max_length=50)
    client_name: str = Field(default="", max_length=255)
    client_cpf: str = Field(default="", max_length=14)
    client_email: str = Field(default="", max_length=255)
    client_phone: str = Field(default="", max_length=20)
    client_role: str = Field(default="NOIVO", max_length=50)
    days_before_in_progress: int = Field(default=7, ge=0)


class WeddingProposalIn(Schema):
    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    groom_name: str = Field(..., min_length=1, max_length=100)
    bride_name: str = Field(..., min_length=1, max_length=100)
    date: datetime.date
    location: str = Field(default="", max_length=255)
    expected_guests: int | None = Field(default=None, ge=1)
    template: str | None = Field(default=None, max_length=50)
    client_name: str = Field(default="", max_length=255)
    client_cpf: str = Field(default="", max_length=14)
    client_email: str = Field(default="", max_length=255)
    client_phone: str = Field(default="", max_length=20)
    client_role: str = Field(default="NOIVO", max_length=50)
    days_before_in_progress: int = Field(default=7, ge=0)


class WeddingPatchIn(Schema):
    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    groom_name: str | None = Field(None, min_length=1, max_length=100)
    bride_name: str | None = Field(None, min_length=1, max_length=100)
    date: datetime.date | None = None
    location: str | None = Field(None, min_length=1, max_length=255)
    expected_guests: int | None = Field(None, ge=1)
    status: WeddingStatusEnum | None = None
    client_name: str | None = Field(None, max_length=255)
    client_cpf: str | None = Field(None, max_length=14)
    client_email: str | None = Field(None, max_length=255)
    client_phone: str | None = Field(None, max_length=20)
    client_role: str | None = Field(None, max_length=50)
    days_before_in_progress: int | None = Field(None, ge=0)


class ConvertToPlanningIn(Schema):
    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    category_id: UUID4 | None = None


class WeddingParticipantRoleEnum(StrEnum):
    BRIDE = "BRIDE"
    GROOM = "GROOM"
    FINANCIAL_PAYER = "FINANCIAL_PAYER"
    LEGAL_REPRESENTATIVE = "LEGAL_REPRESENTATIVE"
    OTHER = "OTHER"


class WeddingParticipantIn(Schema):
    """Schema de entrada para vincular um cliente a um casamento."""

    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    client_id: UUID4
    role: WeddingParticipantRoleEnum | str = WeddingParticipantRoleEnum.BRIDE
    is_primary_signatory: bool = False
    notes: str = ""


class WeddingParticipantOut(Schema):
    """Schema de saída para representação de participantes do casamento."""

    uuid: UUID4
    client_id: UUID4
    client_name: str
    client_cpf: str = ""
    client_email: str = ""
    client_phone: str = ""
    role: str
    role_display: str = ""
    is_primary_signatory: bool = False
    notes: str = ""
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @staticmethod
    def resolve_client_id(obj: Any) -> Any:
        if hasattr(obj, "client") and hasattr(obj.client, "uuid"):
            return obj.client.uuid
        return getattr(obj, "client_id", None)

    @staticmethod
    def resolve_client_name(obj: Any) -> str:
        if hasattr(obj, "client") and hasattr(obj.client, "name"):
            return str(obj.client.name)
        return ""

    @staticmethod
    def resolve_client_cpf(obj: Any) -> str:
        if hasattr(obj, "client") and hasattr(obj.client, "cpf"):
            return str(obj.client.cpf)
        return ""

    @staticmethod
    def resolve_client_email(obj: Any) -> str:
        if hasattr(obj, "client") and hasattr(obj.client, "email"):
            return str(obj.client.email)
        return ""

    @staticmethod
    def resolve_client_phone(obj: Any) -> str:
        if hasattr(obj, "client") and hasattr(obj.client, "phone"):
            return str(obj.client.phone)
        return ""

    @staticmethod
    def resolve_role_display(obj: Any) -> str:
        if hasattr(obj, "get_role_display"):
            return str(obj.get_role_display())
        return str(getattr(obj, "role", ""))


class WeddingOut(Schema):
    uuid: UUID4
    groom_name: str
    bride_name: str
    date: datetime.date
    location: str
    expected_guests: int | None
    status: WeddingStatusEnum
    template: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    total_budget: Decimal | None = Field(None, ge=0)
    overdue_installments: int = Field(0, ge=0)
    incomplete_tasks: int = Field(0, ge=0)
    allowed_transitions: list[str] = Field(default_factory=list)
    can_complete: bool = False
    client_name: str = ""
    client_cpf: str = ""
    client_email: str = ""
    client_phone: str = ""
    client_role: str = ""
    days_before_in_progress: int = 7
    planner_contract: PlannerContractOut | None = None
    participants: list[WeddingParticipantOut] = Field(default_factory=list)

    @staticmethod
    def resolve_participants(obj: "Wedding") -> list[Any]:
        if hasattr(obj, "participants"):
            try:
                return list(obj.participants.all())
            except Exception:
                return []
        return []

    @staticmethod
    def resolve_allowed_transitions(obj: "Wedding") -> list[str]:
        return [
            t.value if hasattr(t, "value") else str(t)
            for t in obj.ALLOWED_TRANSITIONS.get(obj.status, [])
        ]

    @staticmethod
    def resolve_can_complete(obj: "Wedding") -> bool:
        if hasattr(obj, "can_transition_to"):
            return bool(obj.can_transition_to("COMPLETED"))
        return False

    @staticmethod
    def resolve_planner_contract(obj: "Wedding") -> Any | None:
        try:
            return getattr(obj, "planner_contract", None)
        except Exception:
            return None


class WeddingLookupOut(Schema):
    uuid: UUID4
    groom_name: str
    bride_name: str


class WeddingByMonthOut(Schema):
    month: int = Field(..., ge=1, le=12)
    count: int = Field(..., ge=0)
