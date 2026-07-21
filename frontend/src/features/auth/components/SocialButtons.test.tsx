import { describe, expect, it } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { SocialButtons } from "@/features/auth/components/SocialButtons";
import { server } from "@/mocks/server";
import { getAuthGoogleLoginMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";
import type { TokenOut } from "@/api/generated/v1/models/tokenOut";
import { toast } from "sonner";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const mockNavigate = (globalThis as any).__MOCK_NAVIGATE__;

describe("SocialButtons", () => {
  it("renders Google button", () => {
    render(<SocialButtons />);

    expect(screen.getByText("Google Login")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Google Login" }),
    ).toBeInTheDocument();
  });

  it("executes Google login flow and navigates to /dashboard on success", async () => {
    const mockToken: TokenOut = {
      access: "access-token-google",
      refresh: "refresh-token-google",
      user: {
        id: 2,
        first_name: "GoogleUser",
        last_name: "Test",
        email: "googleuser@test.com",
      },
    };
    server.use(getAuthGoogleLoginMockHandler(mockToken));

    render(<SocialButtons />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Google Login" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Bem-vindo, GoogleUser!");
      expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("shows error toast on Google login failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/auth/google/", () =>
        HttpResponse.json(
          { detail: "Token do Google inválido." },
          { status: 400 },
        ),
      ),
    );

    render(<SocialButtons />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Google Login" }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Token do Google inválido.");
    });
  });

  it("shows error toast when Google OAuth widget triggers onError", async () => {
    render(<SocialButtons />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Google Error" }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        "Falha na autenticação com o Google.",
      );
    });
  });
});
