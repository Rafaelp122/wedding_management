import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import LoginPage from "@/features/auth/pages/LoginPage";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

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
    const user = userEvent.setup();
    server.use(
      http.post("*/api/v1/auth/token/", () => {
        return HttpResponse.json({
          access: "access-token-123",
          refresh: "refresh-token-123",
          user: {
            id: 1,
            uuid: "user-1",
            first_name: "Helena",
            last_name: "Silva",
            email: "helena@simaceito.com",
          },
        });
      })
    );

    render(<LoginPage />);

    await user.type(screen.getByRole("textbox", { name: /endereço de e-mail/i }), "helena@simaceito.com");
    await user.type(screen.getByLabelText(/senha de acesso/i), "senha123456");

    await user.click(screen.getByRole("button", { name: /acessar painel/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenLastCalledWith("/dashboard");
    });
  });
});
