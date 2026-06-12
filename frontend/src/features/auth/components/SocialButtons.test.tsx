import { describe, expect, it } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { SocialButtons } from "@/features/auth/components/SocialButtons";

import { toast } from "sonner";

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

    expect(toast.info).toHaveBeenCalledWith(
      "Integração Google SSO em desenvolvimento.",
    );
  });
});
