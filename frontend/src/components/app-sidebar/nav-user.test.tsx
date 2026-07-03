import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { NavUser } from "./nav-user";

// Mock useSidebar as it's needed for NavUser
vi.mock("@/components/ui/sidebar", () => ({
  useSidebar: () => ({
    state: "expanded",
    open: true,
    setOpen: vi.fn(),
    openMobile: false,
    setOpenMobile: vi.fn(),
    isMobile: false,
    toggleSidebar: vi.fn(),
  }),
}));

// Mock useAuthStore
vi.mock("@/stores/authStore", () => ({
  useAuthStore: () => ({
    user: { first_name: "Helena", last_name: "Silva", email: "helena@simaceito.com" },
    logout: vi.fn(),
  }),
}));

describe("NavUser", () => {
  it("renders theme toggle with tooltip in expanded state", async () => {
    const user = userEvent.setup();
    render(<NavUser />);

    const themeButton = screen.getByLabelText("Alternar tema");
    expect(themeButton).toBeInTheDocument();

    await user.hover(themeButton);
    await waitFor(() => {
      expect(screen.getByRole("tooltip", { name: "Alternar tema" })).toBeInTheDocument();
    });
  });
});
