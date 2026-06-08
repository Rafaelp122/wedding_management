import { describe, expect, it } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { PasswordInput } from "@/features/auth/components/PasswordInput";

describe("PasswordInput", () => {
  it("renders password input with placeholder", () => {
    render(<PasswordInput id="test-pw" placeholder="Digite a senha" />);

    const input = screen.getByPlaceholderText("Digite a senha");
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute("type", "password");
  });

  it("toggles visibility when eye button is clicked", async () => {
    const user = userEvent.setup();
    render(<PasswordInput id="test-pw" placeholder="Digite a senha" />);

    const input = screen.getByPlaceholderText("Digite a senha");
    expect(input).toHaveAttribute("type", "password");

    const toggleBtn = screen.getByRole("button");
    await user.click(toggleBtn);

    expect(input).toHaveAttribute("type", "text");
  });

  it("toggles back to password on second click", async () => {
    const user = userEvent.setup();
    render(<PasswordInput id="test-pw" placeholder="Digite a senha" />);

    const input = screen.getByPlaceholderText("Digite a senha");
    const toggleBtn = screen.getByRole("button");

    await user.click(toggleBtn);
    expect(input).toHaveAttribute("type", "text");

    await user.click(toggleBtn);
    expect(input).toHaveAttribute("type", "password");
  });

  it("accepts value and onChange props", async () => {
    const user = userEvent.setup();
    render(<PasswordInput id="test-pw" placeholder="Digite a senha" />);

    const input = screen.getByPlaceholderText("Digite a senha");
    await user.type(input, "mypassword");

    expect(input).toHaveValue("mypassword");
  });
});
