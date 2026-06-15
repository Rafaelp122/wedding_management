import { Page, Locator } from "@playwright/test";

export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(private readonly page: Page) {
    this.emailInput = this.page.locator('input[type="email"]');
    this.passwordInput = this.page.getByLabel("Senha de Acesso");
    this.submitButton = this.page.getByRole("button", { name: "Acessar painel" });
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
