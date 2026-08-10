import { describe, expect, it, vi } from "vitest";
import { toast } from "sonner";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import { ResetPasswordPage } from "@/features/auth/pages/ResetPasswordPage";
import { server } from "@/mocks/server";
import { getAuthPasswordResetConfirmMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";
import { HttpResponse, http } from "msw";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const mockNavigate = (globalThis as any).__MOCK_NAVIGATE__;

describe("ResetPasswordPage", () => {
  it("renders error state when uid or token are missing", () => {
    render(<ResetPasswordPage />, {
      initialEntries: ["/reset-password?uid=testuid"], // Missing token
    });

    expect(screen.getByText("Link Inválido")).toBeInTheDocument();
    expect(
      screen.getByText("O link de redefinição de senha é inválido ou expirou. Por favor, solicite um novo link.")
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /solicitar novo link/i })
    ).toHaveAttribute("href", "/forgot-password");
  });

  it("renders the form when uid and token are provided", () => {
    render(<ResetPasswordPage />, {
      initialEntries: ["/reset-password?uid=testuid&token=testtoken"],
    });

    expect(document.title).toContain("Redefinir Senha");
    expect(screen.getByText("Redefinir Senha")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /redefinir senha/i })
    ).toBeInTheDocument();
  });

  it("shows validation error if passwords do not match", async () => {
    render(<ResetPasswordPage />, {
      initialEntries: ["/reset-password?uid=testuid&token=testtoken"],
    });

    const user = userEvent.setup();
    const passwords = screen.getAllByPlaceholderText("••••••••");

    await user.type(passwords[0], "senha12345");
    await user.type(passwords[1], "senha123");

    await user.click(screen.getByRole("button", { name: /redefinir senha/i }));

    await waitFor(() => {
      expect(screen.getByText("As senhas não coincidem.")).toBeInTheDocument();
    });
  });

  it("submits the form and redirects to login on success", async () => {
    server.use(getAuthPasswordResetConfirmMockHandler({ message: "Success" }));

    render(<ResetPasswordPage />, {
      initialEntries: ["/reset-password?uid=testuid&token=testtoken"],
    });

    const user = userEvent.setup();
    const passwords = screen.getAllByPlaceholderText("••••••••");

    await user.type(passwords[0], "senha12345");
    await user.type(passwords[1], "senha12345");

    await user.click(screen.getByRole("button", { name: /redefinir senha/i }));

    await waitFor(() => {
      // The toast is rendered outside the component usually, but we check for the navigation
      expect(mockNavigate).toHaveBeenCalledWith("/login");
    });
  });

  it("shows error when the reset request fails", async () => {
    server.use(
      http.post("*/api/v1/auth/password-reset/confirm/", () => {
        return HttpResponse.json(
          { message: "Token inválido" },
          { status: 400 }
        );
      })
    );

    const toastSpy = vi.spyOn(toast, "error");

    render(<ResetPasswordPage />, {
      initialEntries: ["/reset-password?uid=testuid&token=testtoken"],
    });

    const user = userEvent.setup();
    const passwords = screen.getAllByPlaceholderText("••••••••");

    await user.type(passwords[0], "senha12345");
    await user.type(passwords[1], "senha12345");

    await user.click(screen.getByRole("button", { name: /redefinir senha/i }));

    await waitFor(() => {
      expect(toastSpy).toHaveBeenCalledWith("Token inválido");
    });
  });
});
