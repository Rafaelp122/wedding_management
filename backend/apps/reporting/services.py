"""
Camada de serviços para o módulo de reporting (relatórios e exportações).
"""

from typing import Literal
from uuid import UUID

from apps.reporting.excel_utils import render_wedding_excel
from apps.reporting.pdf_utils import render_wedding_pdf
from apps.reporting.selectors import wedding_report_data_selector
from apps.tenants.models import Company


class ReportGenerationService:
    """
    Serviço de orquestração e exportação de relatórios consolidados do casamento.

    Delega a agregação de dados aos selectors multi-tenant e a diagramação
    visual aos renderizadores especializados (PDF e Excel).
    """

    @classmethod
    def generate_wedding_pdf(
        cls,
        company: Company,
        wedding_uuid: UUID | str,
    ) -> bytes:
        """
        Gera um relatório diagramado completo do casamento em formato PDF.

        Args:
            company: Empresa tenant autenticada.
            wedding_uuid: Identificador único do casamento.

        Returns:
            Bytes do arquivo PDF gerado.
        """
        data = wedding_report_data_selector(
            company=company,
            wedding_uuid=wedding_uuid,
        )
        return render_wedding_pdf(
            wedding=data.wedding,
            overview=data.overview,
            categories=data.categories,
            installments=data.installments,
            contracts=data.contracts,
            tasks=data.tasks,
        )

    @classmethod
    def generate_wedding_excel(
        cls,
        company: Company,
        wedding_uuid: UUID | str,
    ) -> bytes:
        """
        Gera um relatório operacional completo do casamento em planilha Excel (.xlsx).

        Args:
            company: Empresa tenant autenticada.
            wedding_uuid: Identificador único do casamento.

        Returns:
            Bytes do arquivo Excel (.xlsx) gerado.
        """
        data = wedding_report_data_selector(
            company=company,
            wedding_uuid=wedding_uuid,
        )
        return render_wedding_excel(
            wedding=data.wedding,
            overview=data.overview,
            categories=data.categories,
            installments=data.installments,
            contracts=data.contracts,
            tasks=data.tasks,
        )

    @classmethod
    def export_wedding_report(
        cls,
        company: Company,
        wedding_uuid: UUID | str,
        report_format: Literal["pdf", "excel"] = "pdf",
    ) -> tuple[bytes, str, str]:
        """
        Exporta o relatório consolidado do casamento com metadados de transporte HTTP.

        Args:
            company: Empresa tenant autenticada.
            wedding_uuid: Identificador único do casamento.
            report_format: Formato desejado ('pdf' ou 'excel').

        Returns:
            Tupla contendo (file_bytes, content_type, filename).
        """
        uuid_str = str(wedding_uuid)
        if report_format == "excel":
            file_bytes = cls.generate_wedding_excel(
                company=company,
                wedding_uuid=wedding_uuid,
            )
            content_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            filename = f"relatorio-casamento-{uuid_str}.xlsx"
        else:
            file_bytes = cls.generate_wedding_pdf(
                company=company,
                wedding_uuid=wedding_uuid,
            )
            content_type = "application/pdf"
            filename = f"relatorio-casamento-{uuid_str}.pdf"

        return file_bytes, content_type, filename
