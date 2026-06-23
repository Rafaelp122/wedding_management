import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { DollarSign } from "lucide-react";
import { MetricCard } from "./MetricCard";

describe("MetricCard", () => {
  it("renders label and value", () => {
    render(
      <MetricCard label="Test Label" value={42} icon={<DollarSign />} />,
    );
    expect(screen.getByText("Test Label")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
  });

  it("renders statusLabel when provided", () => {
    render(
      <MetricCard
        label="Test"
        value={10}
        icon={<DollarSign />}
        statusLabel="Urgente"
      />,
    );
    expect(screen.getByText("Urgente")).toBeInTheDocument();
  });

  it("renders children when provided", () => {
    render(
      <MetricCard label="Test" value={10} icon={<DollarSign />}>
        <div data-testid="child">Child content</div>
      </MetricCard>,
    );
    expect(screen.getByTestId("child")).toBeInTheDocument();
  });

  it("renders sheetTrigger when provided", () => {
    render(
      <MetricCard
        label="Test"
        value={10}
        icon={<DollarSign />}
        sheetTrigger={<button data-testid="trigger">Abrir</button>}
      />,
    );
    expect(screen.getByTestId("trigger")).toBeInTheDocument();
  });

  it("renders with neutral severity by default", () => {
    render(
      <MetricCard label="Test" value={0} icon={<DollarSign />} />,
    );
    const card = screen.getByText("Test").closest('[class*="border"]');
    expect(card).toBeInTheDocument();
  });
});
