import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { SocialButtons } from "@/features/auth/components/SocialButtons";

const { toastInfo } = vi.hoisted(() => ({
  toastInfo: vi.fn(),
}));

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: {
      ...actual.toast,
      info: toastInfo,
    },
  };
});

describe("SocialButtons", () => {
  it("renders Google button", () => {
    render(<SocialButtons />);

    expect(screen.getByText("Google")).toBeInTheDocument();
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("shows info toast when Google button is clicked", async () => {
    const user = userEvent.setup();
    render(<SocialButtons />);

    await user.click(screen.getByRole("button"));

    expect(toastInfo).toHaveBeenCalledWith(
      "Integração Google SSO em desenvolvimento.",
    );
  });
});
