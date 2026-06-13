import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { NavMain } from "@/components/app-sidebar/nav-main";
import { SidebarProvider } from "@/components/ui/sidebar";
import { Home, Calendar, DollarSign } from "lucide-react";
import type { ReactElement } from "react";

const items = [
  { title: "Dashboard", path: "/", icon: Home },
  { title: "Casamentos", path: "/weddings", icon: Calendar },
  { title: "Finanças", path: "/finances", icon: DollarSign },
];

function renderWithSidebar(ui: ReactElement, initialEntries = ["/"]) {
  return render(
    <SidebarProvider>
      {ui}
    </SidebarProvider>,
    { initialEntries },
  );
}

function getNavLink(name: string): HTMLElement {
  return screen.getByRole("link", { name: new RegExp(name, "i") });
}

describe("NavMain", () => {
  it("renders all menu items", () => {
    renderWithSidebar(<NavMain items={items} />);

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Casamentos")).toBeInTheDocument();
    expect(screen.getByText("Finanças")).toBeInTheDocument();
  });

  it("highlights active item when path matches exactly", () => {
    renderWithSidebar(<NavMain items={items} />, ["/weddings"]);

    const weddingsLink = getNavLink("Casamentos");
    const dashboardLink = getNavLink("Dashboard");

    expect(weddingsLink).toHaveAttribute("data-active", "true");
    expect(dashboardLink).toHaveAttribute("data-active", "false");
  });

  it("highlights active item when path is nested", () => {
    renderWithSidebar(<NavMain items={items} />, ["/weddings/123"]);

    const weddingsLink = getNavLink("Casamentos");

    expect(weddingsLink).toHaveAttribute("data-active", "true");
  });

  it("does not highlight when path does not match", () => {
    renderWithSidebar(<NavMain items={items} />, ["/finances"]);

    const weddingsLink = getNavLink("Casamentos");

    expect(weddingsLink).toHaveAttribute("data-active", "false");
  });

  it("root path '/' only matches exactly '/' and not '/weddings'", () => {
    renderWithSidebar(<NavMain items={items} />, ["/"]);

    const dashboardLink = getNavLink("Dashboard");
    const weddingsLink = getNavLink("Casamentos");

    expect(dashboardLink).toHaveAttribute("data-active", "true");
    expect(weddingsLink).toHaveAttribute("data-active", "false");
  });

  it("root path is not highlighted when visiting a nested route", () => {
    renderWithSidebar(<NavMain items={items} />, ["/weddings"]);

    const dashboardLink = getNavLink("Dashboard");

    expect(dashboardLink).toHaveAttribute("data-active", "false");
  });

  it("renders links with correct hrefs", () => {
    renderWithSidebar(<NavMain items={items} />);

    const links = screen.getAllByRole("link");
    expect(links).toHaveLength(3);
    expect(links[0]).toHaveAttribute("href", "/");
    expect(links[1]).toHaveAttribute("href", "/weddings");
    expect(links[2]).toHaveAttribute("href", "/finances");
  });
});
