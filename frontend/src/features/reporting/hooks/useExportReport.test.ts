import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";
import { server } from "@/test-utils";
import { useExportReport } from "./useExportReport";

describe("useExportReport", () => {
  const weddingUuid = "123e4567-e89b-12d3-a456-426614174000";

  beforeEach(() => {
    vi.clearAllMocks();
    window.URL.createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    window.URL.revokeObjectURL = vi.fn();
  });

  it("exports PDF successfully and triggers download and success toast", async () => {
    const onSuccess = vi.fn();
    server.use(
      http.get("*/api/v1/reports/weddings/:uuid/", () => {
        return new HttpResponse("%PDF-1.4 Mock Binary", {
          headers: { "Content-Type": "application/pdf" },
        });
      }),
    );

    const { result } = renderHook(() => useExportReport({ onSuccess }));

    await act(async () => {
      await result.current.exportReport(weddingUuid, "pdf", "relatorio-teste");
    });

    expect(window.URL.createObjectURL).toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalledWith("Relatório em PDF exportado com sucesso!");
    expect(onSuccess).toHaveBeenCalled();
  });

  it("exports Excel successfully with default filename prefix", async () => {
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

    const { result } = renderHook(() => useExportReport());

    await act(async () => {
      await result.current.exportReport(weddingUuid, "excel");
    });

    expect(window.URL.createObjectURL).toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalledWith("Relatório em Excel exportado com sucesso!");
  });

  it("decodes Blob error response containing JSON message", async () => {
    server.use(
      http.get("*/api/v1/reports/weddings/:uuid/", () => {
        return new HttpResponse(
          JSON.stringify({ message: "Casamento não localizado para este tenant" }),
          {
            status: 404,
            headers: { "Content-Type": "application/json" },
          },
        );
      }),
    );

    const { result } = renderHook(() => useExportReport());

    await act(async () => {
      await result.current.exportReport(weddingUuid, "pdf");
    });

    expect(toast.error).toHaveBeenCalledWith("Casamento não localizado para este tenant");
  });

  it("decodes Blob error response containing JSON detail fallback", async () => {
    server.use(
      http.get("*/api/v1/reports/weddings/:uuid/", () => {
        return new HttpResponse(
          JSON.stringify({ detail: "Acesso não autorizado ao relatório" }),
          {
            status: 403,
            headers: { "Content-Type": "application/json" },
          },
        );
      }),
    );

    const { result } = renderHook(() => useExportReport());

    await act(async () => {
      await result.current.exportReport(weddingUuid, "pdf");
    });

    expect(toast.error).toHaveBeenCalledWith("Acesso não autorizado ao relatório");
  });

  it("handles Blob error with empty JSON object fallback", async () => {
    server.use(
      http.get("*/api/v1/reports/weddings/:uuid/", () => {
        return new HttpResponse(JSON.stringify({}), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        });
      }),
    );

    const { result } = renderHook(() => useExportReport());

    await act(async () => {
      await result.current.exportReport(weddingUuid, "pdf");
    });

    expect(toast.error).toHaveBeenCalledWith("Não foi possível exportar o relatório. Tente novamente.");
  });

  it("handles Blob error with invalid non-JSON content gracefully", async () => {
    server.use(
      http.get("*/api/v1/reports/weddings/:uuid/", () => {
        return new HttpResponse("Internal Server Crash <html>", {
          status: 500,
          headers: { "Content-Type": "text/html" },
        });
      }),
    );

    const { result } = renderHook(() => useExportReport());

    await act(async () => {
      await result.current.exportReport(weddingUuid, "pdf");
    });

    expect(toast.error).toHaveBeenCalled();
  });

  it("handles non-Blob network error", async () => {
    server.use(
      http.get("*/api/v1/reports/weddings/:uuid/", () => {
        return HttpResponse.error();
      }),
    );

    const { result } = renderHook(() => useExportReport());

    await act(async () => {
      await result.current.exportReport(weddingUuid, "pdf");
    });

    expect(toast.error).toHaveBeenCalled();
  });
});
