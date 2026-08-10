import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import { toast } from "sonner";
import { ForgotPasswordPage } from "@/features/auth/pages/ForgotPasswordPage";
import { server } from "@/mocks/server";
import { getAuthPasswordResetRequestMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";
import { HttpResponse, http } from "msw";

describe("ForgotPasswordPage", () => {
  it("renders the forgot password page", () => {
    render(<ForgotPasswordPage />);

    expect(document.title).toContain("Recuperar Senha");
    expect(screen.getByText("Recuperar Senha")).toBeInTheDocument();
    expect(
      screen.getByText("Esqueceu sua senha? Não se preocupe. Digite seu e-mail abaixo.")
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /enviar link de recuperação/i })).toBeInTheDocument();
  });

  it("submits the form and displays success message", async () => {
    server.use(getAuthPasswordResetRequestMockHandler({ message: "Success" }));

    render(<ForgotPasswordPage />);

    const user = userEvent.setup();
    await user.type(
      screen.getByPlaceholderText("helena@simaceito.com"),
      "helena@simaceito.com"
    );

    await user.click(screen.getByRole("button", { name: /enviar link de recuperação/i }));

    await waitFor(() => {
      expect(screen.getByText("E-mail enviado!")).toBeInTheDocument();
      expect(screen.getByText(/Se o e-mail estiver cadastrado/i)).toBeInTheDocument();
    });
  });

  it("shows an error message when request fails", async () => {
    server.use(
      http.post("*/api/v1/auth/password-reset/request/", () => {
        return HttpResponse.json(
          { message: "Usuário não encontrado" },
          { status: 400 }
        );
      })
    );

    const toastSpy = vi.spyOn(toast, "error");

    render(<ForgotPasswordPage />);

    const user = userEvent.setup();
    await user.type(
      screen.getByPlaceholderText("helena@simaceito.com"),
      "helena@simaceito.com"
    );

    await user.click(screen.getByRole("button", { name: /enviar link de recuperação/i }));

    await waitFor(() => {
      expect(toastSpy).toHaveBeenCalledWith("Usuário não encontrado");
    });
  });
});
