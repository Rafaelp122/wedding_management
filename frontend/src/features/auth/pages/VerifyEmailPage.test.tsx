import { describe, it, expect, vi, beforeEach } from "vitest";
import { VerifyEmailPage } from "./VerifyEmailPage";
import { render, screen, waitFor, userEvent, server } from "@/test-utils";
import { getAuthVerifyEmailMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";
import { http, HttpResponse } from "msw";


const navigateMock = vi.fn();

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

const TestWrapper = () => (
  <VerifyEmailPage />
);

describe("VerifyEmailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    navigateMock.mockClear();
  });

  it("should show invalid state if uid or token is missing", () => {
    render(<TestWrapper />, { initialEntries: ["/verify-email?uid=123"] });

    expect(screen.getByRole("heading", { name: "Erro na Ativação" })).toBeInTheDocument();
    expect(screen.getByText("Link de verificação inválido ou expirado.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reenviar e-mail de ativação" })).toBeInTheDocument();
  });

  it("should verify successfully and show success message", async () => {
    server.use(
      getAuthVerifyEmailMockHandler()
    );

    render(<TestWrapper />, { initialEntries: ["/verify-email?uid=123&token=abc"] });

    expect(screen.getByRole("heading", { name: "Ativando sua conta..." })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Conta Ativada!" })).toBeInTheDocument();
    });

    expect(screen.getByText("Sua conta foi ativada com sucesso! Você já pode acessar a plataforma.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Acessar painel" })).toBeInTheDocument();
  });

  it("should show error state if verification fails", async () => {
    server.use(
      http.post("*/api/v1/auth/verify-email/", () => {
        return HttpResponse.json(
          { message: "Token inválido." },
          { status: 400 }
        );
      })
    );

    render(<TestWrapper />, { initialEntries: ["/verify-email?uid=123&token=abc"] });

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Erro na Ativação" })).toBeInTheDocument();
    });

    const user = userEvent.setup();
    const resendButton = screen.getByRole("button", { name: "Reenviar e-mail de ativação" });
    await user.click(resendButton);

    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledWith("/verify-email-pending");
    });
  });
});
