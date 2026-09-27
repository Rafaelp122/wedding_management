import { describe, it, expect } from "vitest";
import { render, screen } from "@/test-utils";
import ClientsListPage from "./ClientsListPage";

describe("ClientsListPage (Smart Component)", () => {
  it("renderiza o cabeçalho e botão de novo cliente", async () => {
    render(<ClientsListPage />);

    expect(
      await screen.findByRole("heading", { name: /clientes & contatos/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /novo cliente/i })
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/buscar por nome, cpf ou e-mail/i)
    ).toBeInTheDocument();
  });
});
