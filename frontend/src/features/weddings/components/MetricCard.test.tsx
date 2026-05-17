import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { MetricCard } from "@/features/weddings/components/MetricCard";
import { DollarSign } from "lucide-react";

describe("MetricCard", () => {
  it("renders icon, title and value", () => {
    render(
      <MetricCard icon={DollarSign} title="Receita Total" value="R$ 10.000" />,
    );

    expect(screen.getByText("Receita Total")).toBeInTheDocument();
    expect(screen.getByText("R$ 10.000")).toBeInTheDocument();
    // The DollarSign icon is rendered as an SVG
    expect(document.querySelector("svg")).toBeInTheDocument();
  });

  it("renders subtitle when provided", () => {
    render(
      <MetricCard
        icon={DollarSign}
        title="Receita Total"
        value="R$ 10.000"
        subtitle="últimos 30 dias"
      />,
    );

    expect(screen.getByText("últimos 30 dias")).toBeInTheDocument();
  });

  it("does not render subtitle when not provided", () => {
    render(
      <MetricCard icon={DollarSign} title="Receita Total" value="R$ 10.000" />,
    );

    // The subtitle text should not appear in the DOM
    expect(screen.queryByText(/últimos 30 dias/i)).not.toBeInTheDocument();
    // The value rendered as a <p> should still be present
    expect(screen.getByText("R$ 10.000")).toBeInTheDocument();
  });

  it("renders progress bar when progress is provided", () => {
    render(
      <MetricCard
        icon={DollarSign}
        title="Progresso"
        value="75%"
        progress={75}
      />,
    );

    // Radix Progress primitive renders a role="progressbar"
    const progressBar = screen.getByRole("progressbar");
    expect(progressBar).toBeInTheDocument();
  });

  it("does not render progress bar when progress is undefined", () => {
    render(
      <MetricCard icon={DollarSign} title="Progresso" value="75%" />,
    );

    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });

  it("renders numeric value", () => {
    render(
      <MetricCard icon={DollarSign} title="Convidados" value={150} />,
    );

    expect(screen.getByText("150")).toBeInTheDocument();
  });
});
