import { describe, expect, it } from "vitest";
import { render } from "@/test-utils";
import { LoadingScreen } from "./loadingScreen";

describe("LoadingScreen", () => {
  it("renders correctly and contains the spin container", () => {
    const { container } = render(<LoadingScreen />);

    // Check that the spinner element is rendered
    const spinner = container.querySelector(".animate-spin");
    expect(spinner).not.toBeNull();
  });
});
