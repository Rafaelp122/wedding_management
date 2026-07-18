import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { NavUserView } from "./NavUserView";

const mockUser = {
  id: 1,
  uuid: "user-123",
  email: "rafael@example.com",
  first_name: "Rafael",
  last_name: "Silva",
  is_active: true,
  company_id: "company-123",
  created_at: "",
  updated_at: "",
};

describe("NavUserView", () => {
  it("renders user information correctly when expanded", () => {
    render(
      <NavUserView
        user={mockUser}
        theme="light"
        onToggleTheme={vi.fn()}
        isCollapsed={false}
        onNavigate={vi.fn()}
        onLogout={vi.fn()}
      />
    );

    expect(screen.getByText("Rafael Silva")).toBeInTheDocument();
    expect(screen.getByText("rafael@example.com")).toBeInTheDocument();
    expect(screen.getByText("Tema")).toBeInTheDocument();
  });

  it("calls onToggleTheme when the theme button is clicked", async () => {
    const onToggleTheme = vi.fn();
    const user = userEvent.setup();

    render(
      <NavUserView
        user={mockUser}
        theme="light"
        onToggleTheme={onToggleTheme}
        isCollapsed={false}
        onNavigate={vi.fn()}
        onLogout={vi.fn()}
      />
    );

    const themeButton = screen.getByRole("button", { name: /alternar tema/i });
    await user.click(themeButton);

    expect(onToggleTheme).toHaveBeenCalledTimes(1);
  });

  it("calls onNavigate with correct path when Minha Conta is clicked", async () => {
    const onNavigate = vi.fn();
    const user = userEvent.setup();

    render(
      <NavUserView
        user={mockUser}
        theme="light"
        onToggleTheme={vi.fn()}
        isCollapsed={false}
        onNavigate={onNavigate}
        onLogout={vi.fn()}
      />
    );

    const triggerButton = screen.getByRole("button", { name: /menu do usuário/i });
    await user.click(triggerButton);

    const minhaContaItem = screen.getByText("Minha Conta");
    await user.click(minhaContaItem);

    expect(onNavigate).toHaveBeenCalledWith("/settings");
  });

  it("calls onNavigate with correct path when Configurações is clicked", async () => {
    const onNavigate = vi.fn();
    const user = userEvent.setup();

    render(
      <NavUserView
        user={mockUser}
        theme="light"
        onToggleTheme={vi.fn()}
        isCollapsed={false}
        onNavigate={onNavigate}
        onLogout={vi.fn()}
      />
    );

    const triggerButton = screen.getByRole("button", { name: /menu do usuário/i });
    await user.click(triggerButton);

    const configuracoesItem = screen.getByText("Configurações");
    await user.click(configuracoesItem);

    expect(onNavigate).toHaveBeenCalledWith("/settings");
  });

  it("calls onLogout when Sair is clicked", async () => {
    const onLogout = vi.fn();
    const user = userEvent.setup();

    render(
      <NavUserView
        user={mockUser}
        theme="light"
        onToggleTheme={vi.fn()}
        isCollapsed={false}
        onNavigate={vi.fn()}
        onLogout={onLogout}
      />
    );

    const triggerButton = screen.getByRole("button", { name: /menu do usuário/i });
    await user.click(triggerButton);

    const sairItem = screen.getByText("Sair");
    await user.click(sairItem);

    expect(onLogout).toHaveBeenCalledTimes(1);
  });

  it("renders and handles dropdown when collapsed", async () => {
    const user = userEvent.setup();
    render(
      <NavUserView
        user={mockUser}
        theme="dark"
        onToggleTheme={vi.fn()}
        isCollapsed={true}
        onNavigate={vi.fn()}
        onLogout={vi.fn()}
      />
    );

    // Deve exibir o avatar com a inicial
    const avatarButton = screen.getByRole("button", { name: /menu do usuário/i });
    expect(avatarButton).toHaveTextContent("R");

    // Ao clicar no avatar, abre o menu e exibe as informações
    await user.click(avatarButton);
    expect(screen.getByText("Rafael Silva")).toBeInTheDocument();
    expect(screen.getByText("rafael@example.com")).toBeInTheDocument();
  });
});
