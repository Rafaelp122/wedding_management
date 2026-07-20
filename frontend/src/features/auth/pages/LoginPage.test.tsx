import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import LoginPage from "@/features/auth/pages/LoginPage";

describe("LoginPage", () => {
  it("renders the login page layout with hero details and login form", () => {
    render(<LoginPage />);

    // Check page title hook execution / page content
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
});
