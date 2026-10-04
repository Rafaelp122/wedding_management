"""
Camada de serviços para o módulo de reporting (relatórios e exportações).
"""

from typing import Literal
from uuid import UUID

from apps.reporting.selectors import wedding_report_data_selector
from apps.tenants.models import Company


class ReportGenerationService:
    """Serviço de orquestração e exportação de relatórios consolidados do casamento.

    Delega a agregação de dados aos selectors multitenant e a diagramação
    visual aos renderizadores especializados (PDF ReportLab e Excel openpyxl).

    Regras de Negócio e SSOT:
    - Hub do Domínio de Relatórios (BR-R01..04):
      docs/architecture/domains/reporting-domain.md
    - Padrão Query Selectors:
      docs/architecture/concepts/query-selectors-pattern.md
    """

    @classmethod
    def generate_wedding_pdf(
        cls,
        company: Company,
        wedding_uuid: UUID | str,
    ) -> bytes:
        """Gera um relatório diagramado completo do casamento em formato PDF.

        Efeitos Colaterais:
            - Renderiza binário PDF em memória via ReportLab sem persistência em disco.

        Args:
            wedding_uuid: Identificador único do casamento a ser consolidado.

        Returns:
            Conteúdo binário do documento PDF gerado.
        """
        from apps.reporting.pdf_utils import render_wedding_pdf

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
        """Gera um relatório operacional completo do casamento em planilha Excel (.xlsx).

        Efeitos Colaterais:
            - Renderiza binário Excel (.xlsx) em memória via openpyxl sem persistência em disco.

        Args:
            wedding_uuid: Identificador único do casamento a ser consolidado.

        Returns:
            Conteúdo binário da pasta de trabalho Excel (.xlsx) gerada.
        """
        from apps.reporting.excel_utils import render_wedding_excel

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
        """Exporta o relatório consolidado do casamento com metadados de transporte HTTP.

        Efeitos Colaterais:
            - Gera o binário do relatório em memória (PDF ou Excel) delegando aos renderizadores especializados.

        Args:
            wedding_uuid: Identificador único do casamento a ser consolidado.
            report_format: Formato de exportação desejado ('pdf' ou 'excel').

        Returns:
            Tupla contendo o binário do arquivo, o MIME content-type HTTP e o nome sugerido para download.
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
