"""
Utilitários, estilos e renderizador ReportLab para relatórios em PDF (DESIGN.md).
"""

import io
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.finances.models import Installment


class NumberedCanvas(canvas.Canvas):  # type: ignore[misc]
    """
    Canvas customizado do ReportLab com suporte a numeração de páginas em dois passos.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict[str, Any]] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int) -> None:
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#52585E"))

        footer_text = f"Página {self._pageNumber} de {page_count}"
        now_str = datetime.now(UTC).strftime("%d/%m/%Y às %H:%M UTC")
        system_text = f"Sim, Aceito! Prestige • Relatório emitido em {now_str}"

        self.drawString(2 * cm, 1.2 * cm, system_text)
        self.drawRightString(A4[0] - 2 * cm, 1.2 * cm, footer_text)

        self.setStrokeColor(colors.HexColor("#E4E4E7"))
        self.setLineWidth(0.5)
        self.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
        self.restoreState()


def get_pdf_palette() -> dict[str, colors.HexColor]:
    """Retorna os tokens de cor oficiais definidos no DESIGN.md."""
    return {
        "primary": colors.HexColor("#7C3AED"),
        "primary_hover": colors.HexColor("#6D28D9"),
        "secondary": colors.HexColor("#F5F3FF"),
        "surface": colors.HexColor("#FAFAFB"),
        "text_primary": colors.HexColor("#1A1C1E"),
        "text_secondary": colors.HexColor("#52585E"),
        "border": colors.HexColor("#E4E4E7"),
        "white": colors.white,
    }


def format_currency_br(val: Decimal | float | int | None) -> str:
    """Formata valor decimal em moeda brasileira (R$ 1.234,56)."""
    if val is None:
        return "R$ 0,00"
    dec = Decimal(str(val))
    return f"R$ {dec:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _build_pdf_header(
    wedding: Any,
    title_style: ParagraphStyle,
    subtitle_style: ParagraphStyle,
    border_color: colors.HexColor,
) -> list[Any]:
    """Constrói o cabeçalho executivo do casamento."""
    couple_names = f"{wedding.groom_name} & {wedding.bride_name}"
    date_str = (
        wedding.date.strftime("%d/%m/%Y") if wedding.date else "Data não definida"
    )
    guests_str = (
        f"{wedding.expected_guests} convidados"
        if wedding.expected_guests
        else "Convidados não informados"
    )
    location_str = wedding.location or "Local não informado"
    status_label = wedding.get_status_display()

    header_info = (
        f"<b>Data:</b> {date_str} &nbsp;|&nbsp; "
        f"<b>Local:</b> {location_str} &nbsp;|&nbsp; "
        f"<b>Esperado:</b> {guests_str} &nbsp;|&nbsp; "
        f"<b>Status:</b> {status_label}"
    )
    return [
        Paragraph(couple_names, title_style),
        Paragraph(header_info, subtitle_style),
        HRFlowable(
            width="100%",
            thickness=1,
            color=border_color,
            spaceBefore=0,
            spaceAfter=12,
        ),
    ]


def _build_pdf_kpis(
    wedding: Any,
    overview: dict[str, Any],
    installments: list[Any],
    kpi_title_style: ParagraphStyle,
    kpi_val_style: ParagraphStyle,
    palette: dict[str, colors.HexColor],
) -> Table:
    """Constrói a grade de cartões de KPI consolidados."""
    budget_obj = getattr(wedding, "budget", None)
    total_budget = budget_obj.total_estimated if budget_obj else Decimal("0.00")
    total_budget_str = format_currency_br(total_budget)
    paid_sum = sum(
        (i.amount for i in installments if i.status == Installment.StatusChoices.PAID),
        Decimal("0.00"),
    )
    pending_sum = sum(
        (
            i.amount
            for i in installments
            if i.status
            in (
                Installment.StatusChoices.PENDING,
                Installment.StatusChoices.OVERDUE,
            )
        ),
        Decimal("0.00"),
    )
    pct_used = overview.get("budget_percentage_used", 0)

    kpi_data = [
        [
            Paragraph("ORÇAMENTO TOTAL", kpi_title_style),
            Paragraph("TOTAL PAGO", kpi_title_style),
            Paragraph("A PAGAR / PENDENTE", kpi_title_style),
            Paragraph("SAÚDE FINANCEIRA", kpi_title_style),
        ],
        [
            Paragraph(f"<b>{total_budget_str}</b>", kpi_val_style),
            Paragraph(f"<b>{format_currency_br(paid_sum)}</b>", kpi_val_style),
            Paragraph(f"<b>{format_currency_br(pending_sum)}</b>", kpi_val_style),
            Paragraph(f"<b>{pct_used}%</b>", kpi_val_style),
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[4.2 * cm, 4.2 * cm, 4.4 * cm, 4.2 * cm])
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), palette["secondary"]),
                ("BOX", (0, 0), (-1, -1), 0.5, palette["border"]),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, palette["border"]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return kpi_table


def _build_pdf_categories_table(
    categories: list[Any],
    cell_style: ParagraphStyle,
    cell_header_style: ParagraphStyle,
    palette: dict[str, colors.HexColor],
) -> Table:
    """Constrói a tabela de categorias orçamentárias."""
    cat_data = [
        [
            Paragraph("Categoria", cell_header_style),
            Paragraph("Verba Alocada", cell_header_style),
            Paragraph("Total Gasto", cell_header_style),
            Paragraph("Saldo Restante", cell_header_style),
            Paragraph("Uso (%)", cell_header_style),
        ]
    ]
    for cat in categories:
        spent = cat.total_spent
        remaining = cat.allocated_budget - spent
        pct = (
            round((spent / cat.allocated_budget) * 100, 1)
            if cat.allocated_budget > 0
            else 0
        )
        cat_data.append(
            [
                Paragraph(cat.name, cell_style),
                Paragraph(format_currency_br(cat.allocated_budget), cell_style),
                Paragraph(format_currency_br(spent), cell_style),
                Paragraph(format_currency_br(remaining), cell_style),
                Paragraph(f"{pct}%", cell_style),
            ]
        )
    if len(cat_data) == 1:
        cat_data.append(
            [
                Paragraph("Nenhuma categoria orçamentária cadastrada.", cell_style),
                Paragraph("—", cell_style),
                Paragraph("—", cell_style),
                Paragraph("—", cell_style),
                Paragraph("—", cell_style),
            ]
        )

    cat_table = Table(
        cat_data, colWidths=[5.5 * cm, 3.0 * cm, 3.0 * cm, 3.2 * cm, 2.3 * cm]
    )
    cat_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), palette["primary"]),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [palette["white"], palette["secondary"]],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, palette["border"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return cat_table


def _build_pdf_installments_table(
    installments: list[Any],
    cell_style: ParagraphStyle,
    cell_header_style: ParagraphStyle,
    palette: dict[str, colors.HexColor],
) -> Table:
    """Constrói a tabela do cronograma de parcelas."""
    inst_data = [
        [
            Paragraph("Despesa / Descrição", cell_header_style),
            Paragraph("Parcela", cell_header_style),
            Paragraph("Vencimento", cell_header_style),
            Paragraph("Valor", cell_header_style),
            Paragraph("Status", cell_header_style),
            Paragraph("Data Pagamento", cell_header_style),
        ]
    ]
    for inst in installments:
        due_str = inst.due_date.strftime("%d/%m/%Y")
        paid_str = inst.paid_date.strftime("%d/%m/%Y") if inst.paid_date else "—"
        status_desc = inst.get_status_display()
        desc = inst.expense.description if inst.expense else "Parcela"
        inst_data.append(
            [
                Paragraph(desc, cell_style),
                Paragraph(f"Nº {inst.installment_number}", cell_style),
                Paragraph(due_str, cell_style),
                Paragraph(format_currency_br(inst.amount), cell_style),
                Paragraph(status_desc, cell_style),
                Paragraph(paid_str, cell_style),
            ]
        )
    if len(inst_data) == 1:
        inst_data.append(
            [
                Paragraph("Nenhuma parcela cadastrada.", cell_style),
                Paragraph("—", cell_style),
                Paragraph("—", cell_style),
                Paragraph("—", cell_style),
                Paragraph("—", cell_style),
                Paragraph("—", cell_style),
            ]
        )

    inst_table = Table(
        inst_data,
        colWidths=[
            5.0 * cm,
            2.0 * cm,
            2.5 * cm,
            2.7 * cm,
            2.5 * cm,
            2.3 * cm,
        ],
    )
    inst_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), palette["primary"]),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [palette["white"], palette["secondary"]],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, palette["border"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return inst_table


def _build_pdf_contracts_table(
    contracts: list[Any],
    cell_style: ParagraphStyle,
    cell_header_style: ParagraphStyle,
    palette: dict[str, colors.HexColor],
) -> Table:
    """Constrói a tabela de contratos e fornecedores."""
    contr_data = [
        [
            Paragraph("Fornecedor", cell_header_style),
            Paragraph("Valor Total", cell_header_style),
            Paragraph("Status do Contrato", cell_header_style),
        ]
    ]
    for contr in contracts:
        sup_name = contr.supplier.name if contr.supplier else "Fornecedor Direto"
        contr_data.append(
            [
                Paragraph(sup_name, cell_style),
                Paragraph(format_currency_br(contr.total_amount), cell_style),
                Paragraph(contr.get_status_display(), cell_style),
            ]
        )
    if len(contr_data) == 1:
        contr_data.append(
            [
                Paragraph("Nenhum contrato cadastrado.", cell_style),
                Paragraph("—", cell_style),
                Paragraph("—", cell_style),
            ]
        )

    contr_table = Table(contr_data, colWidths=[8.0 * cm, 4.5 * cm, 4.5 * cm])
    contr_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), palette["primary"]),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [palette["white"], palette["secondary"]],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, palette["border"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return contr_table


def render_wedding_pdf(
    wedding: Any,
    overview: dict[str, Any],
    categories: list[Any],
    installments: list[Any],
    contracts: list[Any],
    tasks: list[Any],
) -> bytes:
    """
    Renderiza o relatório PDF diagramado do casamento aderente ao DESIGN.md.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.2 * cm,
    )

    palette = get_pdf_palette()
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=palette["text_primary"],
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=palette["text_secondary"],
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=palette["primary"],
        spaceBefore=14,
        spaceAfter=6,
    )
    kpi_title_style = ParagraphStyle(
        "KPITitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=palette["text_secondary"],
    )
    kpi_val_style = ParagraphStyle(
        "KPIValue",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=palette["primary"],
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=palette["text_primary"],
    )
    cell_header_style = ParagraphStyle(
        "TableHeader",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=palette["white"],
    )

    story: list[Any] = []

    # 1. Cabeçalho
    story.extend(
        _build_pdf_header(wedding, title_style, subtitle_style, palette["border"])
    )

    # 2. KPIs
    story.append(
        _build_pdf_kpis(
            wedding,
            overview,
            installments,
            kpi_title_style,
            kpi_val_style,
            palette,
        )
    )
    story.append(Spacer(1, 10))

    # 3. Categorias
    story.append(Paragraph("Distribuição por Categoria Orçamentária", section_style))
    story.append(
        _build_pdf_categories_table(categories, cell_style, cell_header_style, palette)
    )
    story.append(Spacer(1, 10))

    # 4. Parcelas
    story.append(Paragraph("Cronograma de Parcelas & Pagamentos", section_style))
    story.append(
        _build_pdf_installments_table(
            installments, cell_style, cell_header_style, palette
        )
    )
    story.append(Spacer(1, 10))

    # 5. Contratos
    story.append(Paragraph("Contratos & Fornecedores", section_style))
    story.append(
        _build_pdf_contracts_table(contracts, cell_style, cell_header_style, palette)
    )
    story.append(Spacer(1, 10))

    # 6. Checklist de Tarefas
    story.append(Paragraph("Checklist de Tarefas", section_style))
    tasks_completed = sum(1 for t in tasks if t.is_completed)
    tasks_total = len(tasks)
    tasks_pct = round((tasks_completed / tasks_total) * 100) if tasks_total > 0 else 0
    task_summary_text = (
        f"<b>Progresso:</b> {tasks_completed} de {tasks_total} "
        f"tarefas concluídas ({tasks_pct}%)"
    )
    story.append(Paragraph(task_summary_text, subtitle_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
