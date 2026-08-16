"""
QuerySets e Managers customizados para o domínio financeiro.
Implementa métodos encadeáveis para consultas expressivas e reutilizáveis.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce

from apps.tenants.managers import TenantManager, TenantQuerySet


if TYPE_CHECKING:
    from apps.finances.models.budget import Budget
    from apps.finances.models.budget_category import BudgetCategory
    from apps.finances.models.expense import Expense
    from apps.finances.models.installment import Installment  # noqa: F401
    from apps.tenants.models import Company
    from apps.weddings.models import Wedding


class BudgetQuerySet(TenantQuerySet["Budget"]):
    """QuerySet customizado para Budget com métodos encadeáveis."""

    def with_total_spent(self) -> BudgetQuerySet:
        """Anota cada orçamento com o total geral pago."""
        from apps.finances.models.installment import Installment

        return self.annotate(
            _total_overall_spent=Coalesce(
                Sum(
                    "categories__expenses__installments__amount",
                    filter=Q(
                        categories__expenses__installments__status=Installment.StatusChoices.PAID
                    ),
                ),
                Decimal("0.00"),
            )
        )

    def for_wedding(
        self, wedding: Wedding | UUID | str | int | None = None
    ) -> BudgetQuerySet:
        """
        Filtra orçamentos associados a um casamento específico.

        Args:
            wedding: Instância de Wedding, UUID, string ou id numérico.

        Returns:
            BudgetQuerySet filtrado pelo casamento.
        """
        if not wedding:
            return self
        if hasattr(wedding, "_meta"):
            return self.filter(wedding=wedding)
        if hasattr(wedding, "uuid"):
            return self.filter(wedding__uuid=wedding.uuid)
        if isinstance(wedding, int):
            return self.filter(wedding_id=wedding)
        return self.filter(wedding__uuid=wedding)


class BudgetManager(TenantManager["Budget"]):
    """Manager customizado para Budget."""

    def get_queryset(self) -> BudgetQuerySet:
        return BudgetQuerySet(self.model, using=self._db)

    def for_tenant(self, company: Company) -> BudgetQuerySet:
        return self.get_queryset().filter(company=company)

    def with_total_spent(self) -> BudgetQuerySet:
        """Anota cada orçamento com o total geral pago."""
        return self.get_queryset().with_total_spent()

    def for_wedding(
        self, wedding: Wedding | UUID | str | int | None = None
    ) -> BudgetQuerySet:
        """Filtra orçamentos associados a um casamento específico."""
        return self.get_queryset().for_wedding(wedding)


class BudgetCategoryQuerySet(TenantQuerySet["BudgetCategory"]):
    """QuerySet customizado para BudgetCategory com métodos encadeáveis."""

    def with_total_spent(self) -> BudgetCategoryQuerySet:
        """Anota cada categoria com o total pago (soma de parcelas PAID)."""
        from apps.finances.models.installment import Installment

        return self.annotate(
            _total_spent=Coalesce(
                Sum(
                    "expenses__installments__amount",
                    filter=Q(
                        expenses__installments__status=Installment.StatusChoices.PAID
                    ),
                ),
                Decimal("0.00"),
            )
        )

    def for_budget(
        self, budget: Budget | UUID | str | int | None = None
    ) -> BudgetCategoryQuerySet:
        """
        Filtra categorias pertencentes a um orçamento específico.

        Args:
            budget: Instância de Budget, UUID, string ou id numérico.

        Returns:
            BudgetCategoryQuerySet filtrado pelo orçamento.
        """
        if not budget:
            return self
        if hasattr(budget, "_meta"):
            return self.filter(budget=budget)
        if hasattr(budget, "uuid"):
            return self.filter(budget__uuid=budget.uuid)
        if isinstance(budget, int):
            return self.filter(budget_id=budget)
        return self.filter(budget__uuid=budget)

    def for_wedding(
        self, wedding: Wedding | UUID | str | int | None = None
    ) -> BudgetCategoryQuerySet:
        """
        Filtra categorias pertencentes a um casamento específico.

        Args:
            wedding: Instância de Wedding, UUID, string ou id numérico.

        Returns:
            BudgetCategoryQuerySet filtrado pelo casamento.
        """
        if not wedding:
            return self
        if hasattr(wedding, "_meta"):
            return self.filter(wedding=wedding)
        if hasattr(wedding, "uuid"):
            return self.filter(wedding__uuid=wedding.uuid)
        if isinstance(wedding, int):
            return self.filter(wedding_id=wedding)
        return self.filter(wedding__uuid=wedding)


class BudgetCategoryManager(TenantManager["BudgetCategory"]):
    """Manager customizado para BudgetCategory."""

    def get_queryset(self) -> BudgetCategoryQuerySet:
        return BudgetCategoryQuerySet(self.model, using=self._db)

    def for_tenant(self, company: Company) -> BudgetCategoryQuerySet:
        return self.get_queryset().filter(company=company)

    def with_total_spent(self) -> BudgetCategoryQuerySet:
        """Anota cada categoria com o total pago (soma de parcelas PAID)."""
        return self.get_queryset().with_total_spent()

    def for_budget(
        self, budget: Budget | UUID | str | int | None = None
    ) -> BudgetCategoryQuerySet:
        """Filtra categorias pertencentes a um orçamento específico."""
        return self.get_queryset().for_budget(budget)

    def for_wedding(
        self, wedding: Wedding | UUID | str | int | None = None
    ) -> BudgetCategoryQuerySet:
        """Filtra categorias pertencentes a um casamento específico."""
        return self.get_queryset().for_wedding(wedding)


class ExpenseQuerySet(TenantQuerySet["Expense"]):
    """QuerySet customizado para Expense com métodos encadeáveis."""

    def with_details(self) -> ExpenseQuerySet:
        """Anota cada despesa com contagem de parcelas e valores totais."""
        from apps.finances.models.installment import Installment

        return self.select_related("category", "contract", "wedding").annotate(
            installments_count=Count("installments"),
            paid_installments_count=Count(
                "installments",
                filter=Q(installments__status=Installment.StatusChoices.PAID),
            ),
            total_paid=Coalesce(
                Sum(
                    "installments__amount",
                    filter=Q(installments__status=Installment.StatusChoices.PAID),
                ),
                Decimal("0.00"),
            ),
            total_pending=Coalesce(
                Sum(
                    "installments__amount",
                    filter=Q(
                        installments__status__in=[
                            Installment.StatusChoices.PENDING,
                            Installment.StatusChoices.OVERDUE,
                        ]
                    ),
                ),
                Decimal("0.00"),
            ),
        )

    def by_category(
        self, category: BudgetCategory | UUID | str | int | None = None
    ) -> ExpenseQuerySet:
        """
        Filtra despesas pertencentes a uma categoria específica.

        Args:
            category: Instância de BudgetCategory, UUID, string ou id numérico.

        Returns:
            ExpenseQuerySet filtrado pela categoria.
        """
        if not category:
            return self
        if hasattr(category, "_meta"):
            return self.filter(category=category)
        if hasattr(category, "uuid"):
            return self.filter(category__uuid=category.uuid)
        if isinstance(category, int):
            return self.filter(category_id=category)
        return self.filter(category__uuid=category)

    def for_wedding(
        self, wedding: Wedding | UUID | str | int | None = None
    ) -> ExpenseQuerySet:
        """
        Filtra despesas associadas a um casamento específico.

        Args:
            wedding: Instância de Wedding, UUID, string ou id numérico.

        Returns:
            ExpenseQuerySet filtrado pelo casamento.
        """
        if not wedding:
            return self
        if hasattr(wedding, "_meta"):
            return self.filter(wedding=wedding)
        if hasattr(wedding, "uuid"):
            return self.filter(wedding__uuid=wedding.uuid)
        if isinstance(wedding, int):
            return self.filter(wedding_id=wedding)
        return self.filter(wedding__uuid=wedding)

    def in_date_range(
        self,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> ExpenseQuerySet:
        """
        Filtra despesas dentro de um intervalo de datas de criação.

        Args:
            start_date: Data ou datetime inicial (inclusive).
            end_date: Data ou datetime final (inclusive).

        Returns:
            ExpenseQuerySet filtrado pelo período.
        """
        qs = self
        if start_date is not None:
            if isinstance(start_date, datetime):
                qs = qs.filter(created_at__gte=start_date)
            else:
                qs = qs.filter(created_at__date__gte=start_date)
        if end_date is not None:
            if isinstance(end_date, datetime):
                qs = qs.filter(created_at__lte=end_date)
            else:
                qs = qs.filter(created_at__date__lte=end_date)
        return qs


class ExpenseManager(TenantManager["Expense"]):
    """Manager customizado para Expense."""

    def get_queryset(self) -> ExpenseQuerySet:
        return ExpenseQuerySet(self.model, using=self._db)

    def for_tenant(self, company: Company) -> ExpenseQuerySet:
        return self.get_queryset().filter(company=company)

    def with_details(self) -> ExpenseQuerySet:
        """Anota cada despesa com contagem de parcelas e valores totais."""
        return self.get_queryset().with_details()

    def by_category(
        self, category: BudgetCategory | UUID | str | int | None = None
    ) -> ExpenseQuerySet:
        """Filtra despesas pertencentes a uma categoria específica."""
        return self.get_queryset().by_category(category)

    def for_wedding(
        self, wedding: Wedding | UUID | str | int | None = None
    ) -> ExpenseQuerySet:
        """Filtra despesas associadas a um casamento específico."""
        return self.get_queryset().for_wedding(wedding)

    def in_date_range(
        self,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> ExpenseQuerySet:
        """Filtra despesas dentro de um intervalo de datas de criação."""
        return self.get_queryset().in_date_range(
            start_date=start_date, end_date=end_date
        )


class InstallmentQuerySet(TenantQuerySet["Installment"]):
    """QuerySet customizado para Installment com métodos encadeáveis."""

    def pending(self) -> InstallmentQuerySet:
        """
        Filtra parcelas com status pendente (PENDING).

        Returns:
            InstallmentQuerySet com parcelas pendentes.
        """
        from apps.finances.models.installment import Installment

        return self.filter(status=Installment.StatusChoices.PENDING)

    def overdue(self) -> InstallmentQuerySet:
        """
        Filtra parcelas com status atrasado (OVERDUE).

        Returns:
            InstallmentQuerySet com parcelas atrasadas.
        """
        from apps.finances.models.installment import Installment

        return self.filter(status=Installment.StatusChoices.OVERDUE)

    def paid(self) -> InstallmentQuerySet:
        """
        Filtra parcelas com status pago (PAID).

        Returns:
            InstallmentQuerySet com parcelas pagas.
        """
        from apps.finances.models.installment import Installment

        return self.filter(status=Installment.StatusChoices.PAID)

    def due_in_next_days(
        self, days: int = 7, today: date | None = None
    ) -> InstallmentQuerySet:
        """
        Filtra parcelas com vencimento nos próximos N dias da data de referência.

        Args:
            days: Quantidade de dias futuros para a janela de vencimento.
            today: Data de referência (padrão: hoje).

        Returns:
            InstallmentQuerySet filtrado pela janela de vencimento.
        """
        if today is None:
            today = date.today()
        return self.filter(
            due_date__gte=today,
            due_date__lte=today + timedelta(days=days),
        )

    def due_in_range(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> InstallmentQuerySet:
        """
        Filtra parcelas com vencimento dentro de um intervalo de datas.

        Args:
            start_date: Data de vencimento inicial (inclusive).
            end_date: Data de vencimento final (inclusive).

        Returns:
            InstallmentQuerySet filtrado pelo intervalo de vencimento.
        """
        qs = self
        if start_date is not None:
            qs = qs.filter(due_date__gte=start_date)
        if end_date is not None:
            qs = qs.filter(due_date__lte=end_date)
        return qs

    def for_wedding(
        self, wedding: Wedding | UUID | str | int | None = None
    ) -> InstallmentQuerySet:
        """
        Filtra parcelas associadas a um casamento específico.

        Args:
            wedding: Instância de Wedding, UUID, string ou id numérico.

        Returns:
            InstallmentQuerySet filtrado pelo casamento.
        """
        if not wedding:
            return self
        if hasattr(wedding, "_meta"):
            return self.filter(wedding=wedding)
        if hasattr(wedding, "uuid"):
            return self.filter(wedding__uuid=wedding.uuid)
        if isinstance(wedding, int):
            return self.filter(wedding_id=wedding)
        return self.filter(wedding__uuid=wedding)

    def for_expense(
        self, expense: Expense | UUID | str | int | None = None
    ) -> InstallmentQuerySet:
        """
        Filtra parcelas associadas a uma despesa específica.

        Args:
            expense: Instância de Expense, UUID, string ou id numérico.

        Returns:
            InstallmentQuerySet filtrado pela despesa.
        """
        if not expense:
            return self
        if hasattr(expense, "_meta"):
            return self.filter(expense=expense)
        if hasattr(expense, "uuid"):
            return self.filter(expense__uuid=expense.uuid)
        if isinstance(expense, int):
            return self.filter(expense_id=expense)
        return self.filter(expense__uuid=expense)


class InstallmentManager(TenantManager["Installment"]):
    """Manager customizado para Installment."""

    def get_queryset(self) -> InstallmentQuerySet:
        return InstallmentQuerySet(self.model, using=self._db)

    def for_tenant(self, company: Company) -> InstallmentQuerySet:
        return self.get_queryset().filter(company=company)

    def pending(self) -> InstallmentQuerySet:
        """Filtra parcelas com status pendente (PENDING)."""
        return self.get_queryset().pending()

    def overdue(self) -> InstallmentQuerySet:
        """Filtra parcelas com status atrasado (OVERDUE)."""
        return self.get_queryset().overdue()

    def paid(self) -> InstallmentQuerySet:
        """Filtra parcelas com status pago (PAID)."""
        return self.get_queryset().paid()

    def due_in_next_days(
        self, days: int = 7, today: date | None = None
    ) -> InstallmentQuerySet:
        """Filtra parcelas com vencimento nos próximos N dias."""
        return self.get_queryset().due_in_next_days(days=days, today=today)

    def due_in_range(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> InstallmentQuerySet:
        """Filtra parcelas com vencimento dentro de um intervalo de datas."""
        return self.get_queryset().due_in_range(
            start_date=start_date, end_date=end_date
        )

    def for_wedding(
        self, wedding: Wedding | UUID | str | int | None = None
    ) -> InstallmentQuerySet:
        """Filtra parcelas associadas a um casamento específico."""
        return self.get_queryset().for_wedding(wedding)

    def for_expense(
        self, expense: Expense | UUID | str | int | None = None
    ) -> InstallmentQuerySet:
        """Filtra parcelas associadas a uma despesa específica."""
        return self.get_queryset().for_expense(expense)
