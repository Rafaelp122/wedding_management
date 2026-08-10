import { describe, it, expect, vi, beforeEach } from "vitest";
import { toast } from "sonner";
import { VerifyEmailPendingPage } from "./VerifyEmailPendingPage";
import { render, screen, waitFor, userEvent, server } from "@/test-utils";
import { getAuthResendVerificationMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";
import { http, HttpResponse } from "msw";

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: {
      ...actual.toast,
      success: vi.fn(),
      error: vi.fn(),
    },
  };
});

describe("VerifyEmailPendingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render correctly with email from URL", () => {
    render(<VerifyEmailPendingPage />, { initialEntries: ["/verify-email-pending?email=test%40example.com"] });

    expect(screen.getByRole("heading", { name: "Verifique seu e-mail" })).toBeInTheDocument();
    expect(screen.getByText(/test@example\.com/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reenviar e-mail de ativação" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Voltar para o login" })).toBeInTheDocument();
  });

  it("should render correctly without email", () => {
    render(<VerifyEmailPendingPage />, { initialEntries: ["/verify-email-pending"] });

    expect(screen.getByText(/seu endereço de e-mail/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reenviar e-mail de ativação" })).toBeDisabled();
  });

  it("should successfully resend verification email", async () => {
    server.use(
      getAuthResendVerificationMockHandler()
    );

    render(<VerifyEmailPendingPage />, { initialEntries: ["/verify-email-pending?email=test%40example.com"] });

    const user = userEvent.setup();
    const resendButton = screen.getByRole("button", { name: "Reenviar e-mail de ativação" });
    await user.click(resendButton);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Novo e-mail de confirmação enviado com sucesso!");
    });
  });

  it("should handle error when resending fails", async () => {
    server.use(
      http.post("*/api/v1/auth/resend-verification/", () => {
        return HttpResponse.json(
          { message: "E-mail já verificado ou inválido." },
          { status: 400 }
        );
      })
    );

    render(<VerifyEmailPendingPage />, { initialEntries: ["/verify-email-pending?email=test%40example.com"] });

    const user = userEvent.setup();
    const resendButton = screen.getByRole("button", { name: "Reenviar e-mail de ativação" });
    await user.click(resendButton);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("E-mail já verificado ou inválido.");
    });
  });
});
