import logging

from apps.logistics.models import Contract
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class ContractSummaryService:
    @staticmethod
    def pending_contracts_count(*, company: Company) -> int:
        return (
            Contract.objects.for_tenant(company)
            .filter(
                status__in=[
                    Contract.StatusChoices.DRAFT,
                    Contract.StatusChoices.PENDING,
                ]
            )
            .count()
        )

    @staticmethod
    def wedding_contract_stats(
        *, company: Company, wedding: Wedding
    ) -> tuple[int, int]:
        contracts = Contract.objects.for_tenant(company).filter(wedding=wedding)
        total = contracts.exclude(status=Contract.StatusChoices.CANCELED).count()
        signed = contracts.filter(status=Contract.StatusChoices.SIGNED).count()
        return signed, total
