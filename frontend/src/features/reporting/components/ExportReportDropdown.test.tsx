import { describe, expect, it, vi, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { render, screen, userEvent, server, waitFor } from "@/test-utils";
import { ExportReportDropdown } from "./ExportReportDropdown";

describe("ExportReportDropdown", () => {
  const weddingUuid = "123e4567-e89b-12d3-a456-426614174000";

  beforeEach(() => {
    // Mock URL.createObjectURL e URL.revokeObjectURL
    window.URL.createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    window.URL.revokeObjectURL = vi.fn();
  });

  it("renders the export button with default label and icon", () => {
    render(<ExportReportDropdown weddingUuid={weddingUuid} />);

    const button = screen.getByTestId("export-report-dropdown-trigger");
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent("Exportar");
  });

  it("opens the dropdown menu on click displaying PDF and Excel options", async () => {
    const user = userEvent.setup();
    render(<ExportReportDropdown weddingUuid={weddingUuid} />);

    const button = screen.getByTestId("export-report-dropdown-trigger");
    await user.click(button);

    expect(screen.getByTestId("export-pdf")).toBeInTheDocument();
    expect(screen.getByTestId("export-excel")).toBeInTheDocument();
  });

  it("triggers PDF export on click", async () => {
    server.use(
      http.get("*/api/v1/reports/weddings/:uuid/", () => {
        return new HttpResponse("%PDF-1.4 Mock Binary", {
          headers: {
            "Content-Type": "application/pdf",
            "Content-Disposition": `attachment; filename="relatorio-casamento-${weddingUuid}.pdf"`,
          },
        });
      }),
    );

    const user = userEvent.setup();
    render(
      <ExportReportDropdown
        weddingUuid={weddingUuid}
        weddingName="Lucas & Clara"
      />,
    );

    const button = screen.getByTestId("export-report-dropdown-trigger");
    await user.click(button);

    const pdfOption = screen.getByTestId("export-pdf");
    await user.click(pdfOption);

    await waitFor(() => {
      expect(window.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  it("triggers Excel export on click", async () => {
    server.use(
      http.get("*/api/v1/reports/weddings/:uuid/", () => {
        return new HttpResponse("PK\x03\x04 Mock Binary", {
          headers: {
            "Content-Type":
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          },
        });
      }),
    );

    const user = userEvent.setup();
    render(<ExportReportDropdown weddingUuid={weddingUuid} />);

    const button = screen.getByTestId("export-report-dropdown-trigger");
    await user.click(button);

    const excelOption = screen.getByTestId("export-excel");
    await user.click(excelOption);

    await waitFor(() => {
      expect(window.URL.createObjectURL).toHaveBeenCalled();
    });
  });
});
