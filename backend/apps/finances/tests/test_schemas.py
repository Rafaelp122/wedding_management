"""Testes unitários para os schemas Pydantic/Ninja do domínio financeiro (Finances)."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryOut,
    BudgetCategoryPatchIn,
    BudgetIn,
    BudgetOut,
    BudgetPatchIn,
    ExpenseFromDocumentOut,
    ExpenseIn,
    ExpenseOut,
    ExpensePatchIn,
    InstallmentAdjustIn,
    InstallmentIn,
    InstallmentOut,
    InstallmentPatchIn,
)


class Dummy:
    """Objeto simples para simular instâncias de modelos em testes unitários puros."""

    installments_count: int = 0
    paid_installments_count: int = 0
    _state: Any = None

    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)


class TestBudgetSchemas:
    """Testes de validação para schemas de Orçamento (Budget)."""

    def test_budget_in_whitespace_and_validations(self) -> None:
        wedding_id = uuid.uuid4()
        schema = BudgetIn(
            wedding=wedding_id,
            total_estimated=Decimal("15000.00"),
            notes="   Orçamento inicial para casamento   ",
        )
        assert schema.notes == "Orçamento inicial para casamento"
        assert schema.total_estimated == Decimal("15000.00")

    def test_budget_in_rejects_negative_total_estimated(self) -> None:
        wedding_id = uuid.uuid4()
        with pytest.raises(ValidationError) as exc:
            BudgetIn(
                wedding=wedding_id,
                total_estimated=Decimal("-1.00"),
            )
        assert "greater than or equal to 0" in str(exc.value)

    def test_budget_patch_in_validations(self) -> None:
        schema = BudgetPatchIn(
            total_estimated=Decimal("20000.00"),
            notes="   Revisão do teto   ",
        )
        assert schema.notes == "Revisão do teto"
        assert schema.total_estimated == Decimal("20000.00")

        with pytest.raises(ValidationError):
            BudgetPatchIn(total_estimated=Decimal("-50.00"))

    def test_budget_out_serialization_pure(self) -> None:
        budget_uuid = uuid.uuid4()
        wedding_uuid = uuid.uuid4()
        mock_budget = Dummy(
            uuid=budget_uuid,
            wedding=Dummy(uuid=wedding_uuid),
            total_estimated=Decimal("30000.00"),
            _total_overall_spent=Decimal("12500.00"),
            notes="Notas do orçamento",
        )

        out = BudgetOut.from_orm(mock_budget)
        assert out.uuid == budget_uuid
        assert out.wedding == wedding_uuid
        assert out.total_estimated == Decimal("30000.00")
        assert out.total_overall_spent == Decimal("12500.00")
        assert out.notes == "Notas do orçamento"


class TestBudgetCategorySchemas:
    """Testes de validação para schemas de Categoria de Orçamento (BudgetCategory)."""

    def test_budget_category_in_whitespace_and_validations(self) -> None:
        budget_id = uuid.uuid4()
        schema = BudgetCategoryIn(
            budget=budget_id,
            name="   Decoração e Cenografia   ",
            description="   Arranjos florais e iluminação cênica   ",
            allocated_budget=Decimal("5000.00"),
        )
        assert schema.name == "Decoração e Cenografia"
        assert schema.description == "Arranjos florais e iluminação cênica"
        assert schema.allocated_budget == Decimal("5000.00")

    def test_budget_category_in_rejects_empty_name(self) -> None:
        budget_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            BudgetCategoryIn(
                budget=budget_id,
                name="",
                allocated_budget=Decimal("1000.00"),
            )

        with pytest.raises(ValidationError):
            BudgetCategoryIn(
                budget=budget_id,
                name="   ",
                allocated_budget=Decimal("1000.00"),
            )

    def test_budget_category_in_rejects_negative_allocated_budget(self) -> None:
        budget_id = uuid.uuid4()
        with pytest.raises(ValidationError) as exc:
            BudgetCategoryIn(
                budget=budget_id,
                name="Buffet",
                allocated_budget=Decimal("-10.00"),
            )
        assert "greater than or equal to 0" in str(exc.value)

    def test_budget_category_patch_in_validations(self) -> None:
        schema = BudgetCategoryPatchIn(
            name="   Foto e Vídeo   ",
            allocated_budget=Decimal("0.00"),
        )
        assert schema.name == "Foto e Vídeo"
        assert schema.allocated_budget == Decimal("0.00")

        with pytest.raises(ValidationError):
            BudgetCategoryPatchIn(name="")

        with pytest.raises(ValidationError):
            BudgetCategoryPatchIn(allocated_budget=Decimal("-0.01"))

    def test_budget_category_out_serialization_pure(self) -> None:
        cat_uuid = uuid.uuid4()
        wedding_uuid = uuid.uuid4()
        budget_uuid = uuid.uuid4()
        mock_cat = Dummy(
            uuid=cat_uuid,
            wedding=Dummy(uuid=wedding_uuid),
            budget=Dummy(uuid=budget_uuid),
            name="Música",
            description="DJ e Banda",
            allocated_budget=Decimal("8000.00"),
            _total_spent=Decimal("4500.00"),
        )

        out = BudgetCategoryOut.from_orm(mock_cat)
        assert out.uuid == cat_uuid
        assert out.wedding == wedding_uuid
        assert out.budget == budget_uuid
        assert out.name == "Música"
        assert out.allocated_budget == Decimal("8000.00")
        assert out.total_spent == Decimal("4500.00")


class TestExpenseSchemas:
    """Testes de validação para schemas de Despesa (Expense)."""

    def test_expense_in_whitespace_and_validations(self) -> None:
        cat_id = uuid.uuid4()
        schema = ExpenseIn(
            category=cat_id,
            name="   Banda de Jazz   ",
            description="   Show durante a recepção   ",
            estimated_amount=Decimal("3500.00"),
            actual_amount=Decimal("3200.00"),
            num_installments=3,
            first_due_date=date(2026, 10, 1),
        )
        assert schema.name == "Banda de Jazz"
        assert schema.description == "Show durante a recepção"
        assert schema.estimated_amount == Decimal("3500.00")
        assert schema.actual_amount == Decimal("3200.00")
        assert schema.num_installments == 3

    def test_expense_in_rejects_negative_amounts_and_zero_installments(self) -> None:
        cat_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ExpenseIn(
                category=cat_id,
                name="Banda",
                estimated_amount=Decimal("-10.00"),
                actual_amount=Decimal("100.00"),
            )

        with pytest.raises(ValidationError):
            ExpenseIn(
                category=cat_id,
                name="Banda",
                estimated_amount=Decimal("100.00"),
                actual_amount=Decimal("-10.00"),
            )

        with pytest.raises(ValidationError):
            ExpenseIn(
                category=cat_id,
                name="Banda",
                estimated_amount=Decimal("100.00"),
                actual_amount=Decimal("100.00"),
                num_installments=0,
            )

    def test_expense_patch_in_validations(self) -> None:
        schema = ExpensePatchIn(
            name="   Buffet Atualizado   ",
            actual_amount=Decimal("1000.00"),
        )
        assert schema.name == "Buffet Atualizado"

        with pytest.raises(ValidationError):
            ExpensePatchIn(name="")

        with pytest.raises(ValidationError):
            ExpensePatchIn(actual_amount=Decimal("-5.00"))

        with pytest.raises(ValidationError):
            ExpensePatchIn(num_installments=0)

    def test_expense_from_document_out(self) -> None:
        c_id = uuid.uuid4()
        cat_id = uuid.uuid4()
        schema = ExpenseFromDocumentOut(
            name="Fotógrafo",
            contract=c_id,
            actual_amount=Decimal("5000.00"),
            category_uuid=cat_id,
        )
        assert schema.name == "Fotógrafo"
        assert schema.actual_amount == Decimal("5000.00")

    def test_expense_out_status_resolutions_pure_memory(self) -> None:
        exp_uuid = uuid.uuid4()
        wedding_uuid = uuid.uuid4()
        cat_uuid = uuid.uuid4()

        mock_expense = Dummy(
            uuid=exp_uuid,
            wedding=Dummy(uuid=wedding_uuid),
            category=Dummy(uuid=cat_uuid, name="Geral"),
            contract_id=None,
            name="Serviço Geral",
            description="Desc",
            estimated_amount=Decimal("1000.00"),
            actual_amount=Decimal("1000.00"),
            category_name="Geral",
            contract_description=None,
            total_paid=Decimal("0.00"),
            total_pending=Decimal("1000.00"),
            installments_count=0,
            paid_installments_count=0,
        )

        # 1. total = 0 -> PENDING
        out = ExpenseOut.from_orm(mock_expense)
        assert out.status == "PENDING"
        assert out.installments_count == 0
        assert out.paid_installments_count == 0

        # 2. total = 2, paid = 0 -> PENDING
        mock_expense.installments_count = 2
        mock_expense.paid_installments_count = 0
        out = ExpenseOut.from_orm(mock_expense)
        assert out.status == "PENDING"

        # 3. total = 2, paid = 1 -> PARTIALLY_PAID
        mock_expense.installments_count = 2
        mock_expense.paid_installments_count = 1
        out = ExpenseOut.from_orm(mock_expense)
        assert out.status == "PARTIALLY_PAID"

        # 4. total = 2, paid = 2 -> SETTLED
        mock_expense.installments_count = 2
        mock_expense.paid_installments_count = 2
        out = ExpenseOut.from_orm(mock_expense)
        assert out.status == "SETTLED"

    def test_expense_out_contract_resolution_pure(self) -> None:
        contract_uuid = uuid.uuid4()
        mock_contract = Dummy(uuid=contract_uuid, description="Contrato Buffet")

        mock_expense = Dummy(
            uuid=uuid.uuid4(),
            wedding=Dummy(uuid=uuid.uuid4()),
            category=Dummy(uuid=uuid.uuid4(), name="Buffet"),
            contract_id=1,
            name="Despesa",
            description="",
            estimated_amount=Decimal("100.00"),
            actual_amount=Decimal("100.00"),
            category_name="Buffet",
            contract_description=None,
            installments_count=0,
            paid_installments_count=0,
            total_paid=Decimal("0.00"),
            total_pending=Decimal("0.00"),
            _state=Dummy(fields_cache={"contract": mock_contract}),
        )

        out = ExpenseOut.from_orm(mock_expense)
        assert out.contract == contract_uuid
        assert out.contract_description == "Contrato Buffet"

        # Sem cache em fields_cache (não dispara query ad-hoc)
        mock_expense._state = Dummy(fields_cache={})
        out_no_cache = ExpenseOut.from_orm(mock_expense)
        assert out_no_cache.contract is None


class TestInstallmentSchemas:
    """Testes de validação para schemas de Parcela (Installment)."""

    def test_installment_in_whitespace_and_validations(self) -> None:
        exp_id = uuid.uuid4()
        schema = InstallmentIn(
            expense=exp_id,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date(2026, 11, 15),
            notes="   Primeira parcela via PIX   ",
        )
        assert schema.notes == "Primeira parcela via PIX"
        assert schema.installment_number == 1
        assert schema.amount == Decimal("500.00")

    def test_installment_in_rejects_negative_amount_and_zero_number(self) -> None:
        exp_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            InstallmentIn(
                expense=exp_id,
                installment_number=0,
                amount=Decimal("100.00"),
                due_date=date(2026, 11, 15),
            )

        with pytest.raises(ValidationError):
            InstallmentIn(
                expense=exp_id,
                installment_number=1,
                amount=Decimal("-10.00"),
                due_date=date(2026, 11, 15),
            )

    def test_installment_patch_in_validations(self) -> None:
        schema = InstallmentPatchIn(
            installment_number=2,
            amount=Decimal("250.00"),
            notes="   Ajuste parcial   ",
        )
        assert schema.notes == "Ajuste parcial"

        with pytest.raises(ValidationError):
            InstallmentPatchIn(installment_number=0)

        with pytest.raises(ValidationError):
            InstallmentPatchIn(amount=Decimal("-1.00"))

    def test_installment_adjust_in_validations(self) -> None:
        schema = InstallmentAdjustIn(amount=Decimal("300.00"))
        assert schema.amount == Decimal("300.00")

        with pytest.raises(ValidationError):
            InstallmentAdjustIn(amount=Decimal("-0.01"))

    def test_installment_out_serialization_pure(self) -> None:
        inst_uuid = uuid.uuid4()
        wedding_uuid = uuid.uuid4()
        exp_uuid = uuid.uuid4()

        mock_inst = Dummy(
            uuid=inst_uuid,
            wedding=Dummy(uuid=wedding_uuid),
            expense=Dummy(uuid=exp_uuid),
            installment_number=1,
            amount=Decimal("750.00"),
            due_date=date(2026, 12, 1),
            paid_date=None,
            status="PENDING",
            notes="Parcela única",
        )

        out = InstallmentOut.from_orm(mock_inst)
        assert out.uuid == inst_uuid
        assert out.wedding == wedding_uuid
        assert out.expense == exp_uuid
        assert out.installment_number == 1
        assert out.amount == Decimal("750.00")
        assert out.status == "PENDING"
