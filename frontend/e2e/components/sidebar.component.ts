import { Page, Locator } from "@playwright/test";

export class SidebarComponent {
  readonly userMenuButton: Locator;
  readonly logoutButton: Locator;

  constructor(private readonly page: Page) {
    this.userMenuButton = this.page.getByRole("button", { name: "Menu do usuário" });
    this.logoutButton = this.page.getByRole("menuitem", { name: "Sair" });
  }

  async logout() {
    await this.userMenuButton.click();
    await this.logoutButton.click();
  }
}
