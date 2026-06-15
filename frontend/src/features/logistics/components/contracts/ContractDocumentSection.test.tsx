import { describe, expect, it } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { server } from "@/mocks/server";
import { ContractDocumentSection } from "./ContractDocumentSection";

import { toast } from "sonner";

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
          weddingUuid="wedding-1"
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
          weddingUuid="wedding-1"
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
          weddingUuid="wedding-1"
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
          weddingUuid="wedding-1"
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
          weddingUuid="wedding-1"
        />,
      );

      expect(screen.getByRole("button", { name: /enviar/i })).toBeDisabled();
    });
  });

  describe("upload flow", () => {
    it("shows success toast when upload succeeds", async () => {
      const { http, HttpResponse } = await import("msw");
      server.use(
        http.post("*/api/v1/logistics/contracts/upload-url/", () =>
          HttpResponse.json({
            upload_url: "https://r2.com/presigned-url",
            object_key: "r2-file-key",
          }),
        ),
        http.put("https://r2.com/presigned-url", () =>
          new HttpResponse(null, { status: 200 }),
        ),
        http.post("*/api/v1/logistics/contracts/:uuid/upload/", async ({ request }) => {
          const body = (await request.json()) as { pdf_file_key: string };
          expect(body.pdf_file_key).toBe("r2-file-key");
          return HttpResponse.json({ uuid: CONTRACT_UUID }, { status: 200 });
        }),
      );

      const { container } = render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={false}
          fileName={null}
          weddingUuid="wedding-1"
        />,
      );

      const user = userEvent.setup();
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      await user.upload(
        fileInput,
        new File(["dummy content"], FILE_NAME, {
          type: "application/pdf",
        }),
      );

      await user.click(screen.getByRole("button", { name: /enviar/i }));

      await waitFor(
        () => {
          expect(toast.success).toHaveBeenCalledWith(
            "Documento enviado com sucesso!",
          );
        },
        { timeout: 5000 },
      );
    });

    it("shows error toast when upload fails", async () => {
      const { http, HttpResponse } = await import("msw");
      server.use(
        http.post("*/api/v1/logistics/contracts/upload-url/", () =>
          HttpResponse.json({
            upload_url: "https://r2.com/presigned-url",
            object_key: "r2-file-key",
          }),
        ),
        http.put("https://r2.com/presigned-url", () =>
          new HttpResponse(null, { status: 200 }),
        ),
        http.post("*/api/v1/logistics/contracts/:uuid/upload/", () =>
          HttpResponse.json({ detail: "Erro no upload" }, { status: 500 }),
        ),
      );

      const { container } = render(
        <ContractDocumentSection
          contractUuid={CONTRACT_UUID}
          hasFile={false}
          fileName={null}
          weddingUuid="wedding-1"
        />,
      );

      const user = userEvent.setup();
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      await user.upload(
        fileInput,
        new File(["dummy content"], FILE_NAME, {
          type: "application/pdf",
        }),
      );

      await user.click(screen.getByRole("button", { name: /enviar/i }));

      await waitFor(
        () => {
          expect(toast.error).toHaveBeenCalledWith(
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
          weddingUuid="wedding-1"
        />,
      );

      const user = userEvent.setup();
      await user.click(screen.getByRole("button", { name: /remover/i }));

      await waitFor(
        () => {
          expect(toast.success).toHaveBeenCalledWith("Documento removido.");
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
          weddingUuid="wedding-1"
        />,
      );

      const user = userEvent.setup();
      await user.click(screen.getByRole("button", { name: /remover/i }));

      await waitFor(
        () => {
          expect(toast.error).toHaveBeenCalledWith(
            "Erro ao remover documento.",
          );
        },
        { timeout: 5000 },
      );
    });
  });
});
