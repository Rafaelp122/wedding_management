import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, cast

from django.db.models import Q, Sum
from django.utils import timezone

from apps.finances.models import Budget, BudgetCategory, Installment
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class FinancialSummaryService:
    """
    Camada de serviço para consolidação de resumos e relatórios financeiros.
    Agrega informações sobre parcelas pendentes, vencidas, uso de orçamento
    e distribuição de gastos por categorias de orçamento do tenant.
    """

    @staticmethod
    def pending_installments_7d(
        *, company: Company, today: date | None = None
    ) -> Decimal:
        """
        Retorna o valor total de parcelas pendentes que vencem nos próximos 7 dias.

        Args:
            company: O tenant atual para isolamento de dados.
            today: Data de referência (caso não informada, usa a data atual).

        Returns:
            Valor decimal total acumulado das parcelas que vencem em 7 dias.
        """
        today = today or timezone.localdate()
        seven_days = today + timedelta(days=7)
        total = (
            Installment.objects.for_tenant(company)
            .filter(
                status=Installment.StatusChoices.PENDING,
                due_date__gte=today,
                due_date__lte=seven_days,
            )
            .aggregate(total=Sum("amount"))["total"]
        )
        return total or Decimal("0.00")

    @staticmethod
    def overdue_installments(
        *, company: Company, today: date | None = None
    ) -> tuple[Decimal, int]:
        """
        Retorna o valor total acumulado e a quantidade de parcelas atrasadas.

        Considera parcelas com status explícito de atraso (OVERDUE) ou
        pendentes com vencimento anterior à data de referência.

        Args:
            company: O tenant atual para isolamento de dados.
            today: Data de referência (caso não informada, usa a data atual).

        Returns:
            Uma tupla contendo (valor_total_atrasado, quantidade_de_parcelas).
        """
        today = today or timezone.localdate()
        qs = Installment.objects.for_tenant(company).filter(
            Q(status=Installment.StatusChoices.OVERDUE)
            | Q(status=Installment.StatusChoices.PENDING, due_date__lt=today)
        )
        amount = qs.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        return amount, qs.count()

    @staticmethod
    def budget_percentage_used(*, company: Company, wedding: Wedding) -> float:
        """
        Calcula o percentual do orçamento estimado consumido até o momento.

        O percentual retornado é limitado ao teto máximo de 100%.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding: Instância do casamento associado.

        Returns:
            Percentual utilizado (float) arredondado para uma casa decimal.
        """
        try:
            from apps.finances.managers import BudgetQuerySet

            budget = (
                cast(BudgetQuerySet, Budget.objects.for_tenant(company))
                .with_total_spent()
                .get(wedding=wedding)
            )
            total_spent = budget.total_overall_spent
            total_est = budget.total_estimated
            if total_est > 0:
                pct = float(total_spent) / float(total_est) * 100
                return min(100.0, round(pct, 1))
            return 0.0
        except Budget.DoesNotExist:
            return 0.0

    @staticmethod
    def upcoming_installments(
        *, company: Company, wedding: Wedding, today: date | None = None
    ) -> list[dict[str, Any]]:
        """
        Retorna até 5 parcelas a vencer nos próximos 30 dias de um casamento.

        Também inclui parcelas que já estejam vencidas (status OVERDUE).

        Args:
            company: O tenant atual para isolamento de dados.
            wedding: Instância do casamento associado.
            today: Data de referência (caso não informada, usa a data atual).
        """
        today = today or timezone.localdate()
        date_limit = today + timedelta(days=30)

        installments = (
            Installment.objects.for_tenant(company)
            .filter(
                wedding=wedding,
                due_date__lte=date_limit,
            )
            .filter(
                Q(status=Installment.StatusChoices.OVERDUE)
                | Q(status=Installment.StatusChoices.PENDING)
            )
            .order_by("due_date")[:5]
        )
        return [
            {
                "uuid": inst.uuid,
                "installment_number": inst.installment_number,
                "amount": str(inst.amount),
                "due_date": inst.due_date,
                "status": inst.status,
            }
            for inst in installments
        ]

    @staticmethod
    def categories_summary(
        *, company: Company, wedding: Wedding
    ) -> list[dict[str, Any]]:
        """
        Gera um resumo de categorias de orçamento com alocação e gastos.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding: Instância do casamento associado.

        Returns:
            Lista de dicionários contendo o nome da categoria, valor alocado,
            valor gasto e a respectiva porcentagem consumida.
        """
        categories = (
            BudgetCategory.objects.for_tenant(company)
            .filter(wedding=wedding)
            .select_related("budget")
            .with_total_spent()  # type: ignore[attr-defined]
        )
        result = []
        for cat in categories:
            spent = cat.total_spent
            alloc = cat.allocated_budget
            pct = round(float(spent) / float(alloc) * 100) if alloc > 0 else 0
            result.append(
                {
                    "name": cat.name,
                    "allocated": str(alloc),
                    "spent": str(spent),
                    "percentage": min(pct, 100),
                }
            )
        logger.info(
            "Categorias computadas: wedding=%s, total=%s", wedding.uuid, len(result)
        )
        return result
