import { describe, expect, it } from "vitest";

import { render, screen } from "@/test-utils";
import ComingSoonPage from "./coming-soon";

describe("ComingSoonPage", () => {
  it("renders the requested module information", () => {
    render(
      <ComingSoonPage
        title="Configurações"
        description="Preferências da organização."
      />,
    );

    expect(
      screen.getAllByRole("heading", { name: "Configurações" }),
    ).toHaveLength(2);
    expect(screen.getByText("Preferências da organização.")).toBeInTheDocument();
  });
});
