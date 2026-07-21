import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { SocialButtons } from "@/features/auth/components/SocialButtons";
import { server } from "@/mocks/server";
import { getAuthGoogleLoginMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";
import type { TokenOut } from "@/api/generated/v1/models/tokenOut";
import { toast } from "sonner";

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("SocialButtons", () => {
  it("renders Google button", () => {
    render(<SocialButtons />);

    expect(screen.getByText("Google")).toBeInTheDocument();
    expect(screen.getByRole("button")).toBeInTheDocument();
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
    await user.click(screen.getByRole("button"));

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
    await user.click(screen.getByRole("button"));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Token do Google inválido.");
    });
  });
});
