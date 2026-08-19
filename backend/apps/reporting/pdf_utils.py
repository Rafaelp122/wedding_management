"""
Utilitários e canvas customizados do ReportLab para renderização de relatórios em PDF.
"""

from datetime import UTC, datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):  # type: ignore[misc]
    """
    Canvas customizado do ReportLab com contagem total de páginas (Página X de Y).
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
        self.setFillColor(colors.HexColor("#71717A"))

        # Rodapé inferior
        footer_text = f"Página {self._pageNumber} de {page_count}"
        now_str = datetime.now(UTC).strftime("%d/%m/%Y às %H:%M UTC")
        system_text = f"Wedding Management • Relatório emitido em {now_str}"

        self.drawString(2 * cm, 1.2 * cm, system_text)
        self.drawRightString(A4[0] - 2 * cm, 1.2 * cm, footer_text)

        # Linha separadora do rodapé
        self.setStrokeColor(colors.HexColor("#E4E4E7"))
        self.setLineWidth(0.5)
        self.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
        self.restoreState()
