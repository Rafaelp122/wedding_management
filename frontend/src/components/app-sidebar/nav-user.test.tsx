import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { NavUser } from "./nav-user";
import { useSidebar } from "@/components/ui/sidebar";
import { useAuthStore } from "@/stores/authStore";

// Mock useSidebar
vi.mock("@/components/ui/sidebar", () => ({
  useSidebar: vi.fn(),
}));

// Mock useAuthStore
vi.mock("@/stores/authStore", () => ({
  useAuthStore: vi.fn(),
}));

describe("NavUser", () => {
  it("renders theme toggle with tooltip in expanded state", async () => {
    vi.mocked(useSidebar).mockReturnValue({
      state: "expanded",
      open: true,
      setOpen: vi.fn(),
      openMobile: false,
      setOpenMobile: vi.fn(),
      isMobile: false,
      toggleSidebar: vi.fn(),
    } as any);

    vi.mocked(useAuthStore).mockReturnValue({
      user: { first_name: "Helena", last_name: "Silva", email: "helena@simaceito.com" },
      logout: vi.fn(),
    } as any);

    const user = userEvent.setup();
    render(<NavUser />);

    const themeButton = screen.getByLabelText("Alternar tema");
    expect(themeButton).toBeInTheDocument();

    await user.hover(themeButton);
    await waitFor(() => {
      expect(screen.getByRole("tooltip", { name: "Alternar tema" })).toBeInTheDocument();
    });

    await user.click(themeButton);
  });

  it("renders user avatar in collapsed state", async () => {
    vi.mocked(useSidebar).mockReturnValue({
      state: "collapsed",
      open: false,
      setOpen: vi.fn(),
      openMobile: false,
      setOpenMobile: vi.fn(),
      isMobile: false,
      toggleSidebar: vi.fn(),
    } as any);

    vi.mocked(useAuthStore).mockReturnValue({
      user: { first_name: "Helena", last_name: "Silva", email: "helena@simaceito.com" },
      logout: vi.fn(),
    } as any);

    render(<NavUser />);

    const avatarTrigger = screen.getByLabelText("Menu do usuário");
    expect(avatarTrigger).toBeInTheDocument();
    expect(screen.getByText("H")).toBeInTheDocument();
  });
});
