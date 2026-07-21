import { describe, expect, it } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import LoginPage from "@/features/auth/pages/LoginPage";
import { server } from "@/mocks/server";
import { getAuthObtainTokenMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const mockNavigate = (globalThis as any).__MOCK_NAVIGATE__;

describe("LoginPage", () => {
  it("renders the login page layout with hero details, title and login form", () => {
    render(<LoginPage />);

    expect(document.title).toContain("Entrar");
    expect(
      screen.getByText(
        "O verdadeiro luxo reside na ausência absoluta de falhas logísticas e orçamentais nos bastidores.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Júlia & Marcos")).toBeInTheDocument();
    expect(screen.getByText("Acesse sua plataforma")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /acessar painel/i }),
    ).toBeInTheDocument();
  });

  it("submits login form and navigates to dashboard on success", async () => {
    const mockToken = {
      access: "access-token-123",
      refresh: "refresh-token-123",
      user: {
        id: 1,
        first_name: "Helena",
        last_name: "Silva",
        email: "helena@simaceito.com",
      },
    };
    server.use(getAuthObtainTokenMockHandler(mockToken));

    render(<LoginPage />);

    const user = userEvent.setup();
    await user.type(
      screen.getByPlaceholderText("helena@simaceito.com"),
      "helena@simaceito.com",
    );
    await user.type(screen.getByPlaceholderText("••••••••"), "senha123456");

    await user.click(screen.getByRole("button", { name: /acessar painel/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
    });
  });
});
