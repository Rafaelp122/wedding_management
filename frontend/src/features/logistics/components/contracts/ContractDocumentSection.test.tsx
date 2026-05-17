import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { fireEvent } from "@testing-library/react";
import { server } from "@/mocks/server";
import { ContractDocumentSection } from "./ContractDocumentSection";

const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: {
      ...actual.toast,
      success: toastSuccess,
      error: toastError,
    },
  };
});

const CONTRACT_UUID = "c-1";
const FILE_NAME = "Contrato_Assinado.pdf";

describe("ContractDocumentSection", () => {
  describe("when hasFile is true", () => {
    it("renders the file name when fileName is provided", () => {
      render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={true}
          fileName={FILE_NAME}
        />,
      );

      expect(screen.getByText(FILE_NAME)).toBeInTheDocument();
    });

    it("shows remove button when file exists", () => {
      render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={true}
          fileName={FILE_NAME}
        />,
      );

      expect(
        screen.getByRole("button", { name: /remover/i }),
      ).toBeInTheDocument();
    });
  });

  describe("when hasFile is false", () => {
    it("shows file upload input", () => {
      const { container } = render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={false}
          fileName={null}
        />,
      );

      expect(container.querySelector('input[type="file"]')).toBeInTheDocument();
    });

    it('shows "Enviar" button when no file exists', () => {
      render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={false}
          fileName={null}
        />,
      );

      expect(
        screen.getByRole("button", { name: /enviar/i }),
      ).toBeInTheDocument();
    });

    it('"Enviar" button is disabled when no file is selected', () => {
      render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={false}
          fileName={null}
        />,
      );

      expect(screen.getByRole("button", { name: /enviar/i })).toBeDisabled();
    });
  });

  describe("upload flow", () => {
    it("shows success toast when upload succeeds", async () => {
      const { container } = render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={false}
          fileName={null}
        />,
      );

      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: [
            new File(["dummy content"], FILE_NAME, {
              type: "application/pdf",
            }),
          ],
        },
      });

      const user = userEvent.setup();
      await user.click(screen.getByRole("button", { name: /enviar/i }));

      await waitFor(
        () => {
          expect(toastSuccess).toHaveBeenCalledWith(
            "Documento enviado com sucesso!",
          );
        },
        { timeout: 5000 },
      );
    });

    it("shows error toast when upload fails", async () => {
      const { http, HttpResponse } = await import("msw");
      server.use(
        http.post("*/api/v1/logistics/contracts/:uuid/upload/", () =>
          HttpResponse.json({ detail: "Erro no upload" }, { status: 500 }),
        ),
      );

      const { container } = render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={false}
          fileName={null}
        />,
      );

      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: [
            new File(["dummy content"], FILE_NAME, {
              type: "application/pdf",
            }),
          ],
        },
      });

      const user = userEvent.setup();
      await user.click(screen.getByRole("button", { name: /enviar/i }));

      await waitFor(
        () => {
          expect(toastError).toHaveBeenCalledWith(
            "Erro ao enviar documento.",
          );
        },
        { timeout: 5000 },
      );
    });
  });

  describe("remove flow", () => {
    it("shows success toast when remove succeeds", async () => {
      render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={true}
          fileName={FILE_NAME}
        />,
      );

      const user = userEvent.setup();
      await user.click(screen.getByRole("button", { name: /remover/i }));

      await waitFor(
        () => {
          expect(toastSuccess).toHaveBeenCalledWith("Documento removido.");
        },
        { timeout: 5000 },
      );
    });

    it("shows error toast when remove fails", async () => {
      const { http, HttpResponse } = await import("msw");
      server.use(
        http.delete("*/api/v1/logistics/contracts/:uuid/upload/", () =>
          HttpResponse.json({ detail: "Erro ao remover" }, { status: 500 }),
        ),
      );

      render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={true}
          fileName={FILE_NAME}
        />,
      );

      const user = userEvent.setup();
      await user.click(screen.getByRole("button", { name: /remover/i }));

      await waitFor(
        () => {
          expect(toastError).toHaveBeenCalledWith(
            "Erro ao remover documento.",
          );
        },
        { timeout: 5000 },
      );
    });
  });
});
