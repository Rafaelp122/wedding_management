import { describe, expect, it } from "vitest";
import { render } from "@/test-utils";
import { ProgressBar } from "./ProgressBar";

describe("ProgressBar", () => {
  it("renders with correct percentage width", () => {
    const { container } = render(<ProgressBar percentage={45} />);
    const bar = container.querySelector('[style*="width"]');
    expect(bar).toHaveStyle("width: 45%");
  });

  it("renders with destructive color when >= 90%", () => {
    const { container } = render(<ProgressBar percentage={90} />);
    const bar = container.querySelector('[style*="width"]');
    expect(bar?.className).toContain("bg-destructive");
  });

  it("renders with amber color when >= 70%", () => {
    const { container } = render(<ProgressBar percentage={75} />);
    const bar = container.querySelector('[style*="width"]');
    expect(bar?.className).toContain("bg-amber-500");
  });

  it("renders with aura color when < 70%", () => {
    const { container } = render(<ProgressBar percentage={50} />);
    const bar = container.querySelector('[style*="width"]');
    expect(bar?.className).toContain("bg-aura-500");
  });

  it("caps at 100% width", () => {
    const { container } = render(<ProgressBar percentage={150} />);
    const bar = container.querySelector('[style*="width"]');
    expect(bar).toHaveStyle("width: 100%");
  });

  it("accepts custom className", () => {
    const { container } = render(
      <ProgressBar percentage={50} className="custom-track" />,
    );
    const track = container.firstElementChild;
    expect(track?.className).toContain("custom-track");
  });
});
