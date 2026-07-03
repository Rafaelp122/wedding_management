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

// Mock next-themes partially
const setThemeMock = vi.fn();
vi.mock("next-themes", async (importOriginal) => {
  const actual = await importOriginal<typeof import("next-themes")>();
  return {
    ...actual,
    useTheme: () => ({
      theme: "light",
      setTheme: setThemeMock,
    }),
  };
});

// Mock react-router-dom
const navigateMock = vi.fn();
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

// Helper to mock return values without 'any'
const mockSidebar = (overrides = {}) => {
  vi.mocked(useSidebar).mockReturnValue({
    state: "expanded",
    open: true,
    setOpen: vi.fn(),
    openMobile: false,
    setOpenMobile: vi.fn(),
    isMobile: false,
    toggleSidebar: vi.fn(),
    ...overrides,
  } as ReturnType<typeof useSidebar>);
};

const mockAuth = (overrides = {}) => {
  vi.mocked(useAuthStore).mockReturnValue({
    user: { first_name: "Helena", last_name: "Silva", email: "helena@simaceito.com" },
    logout: vi.fn(),
    login: vi.fn(),
    ...overrides,
  } as unknown as ReturnType<typeof useAuthStore>);
};

describe("NavUser", () => {
  it("renders theme toggle with tooltip in expanded state", async () => {
    mockSidebar({ state: "expanded" });
    mockAuth();

    const user = userEvent.setup();
    render(<NavUser />);

    const themeButton = screen.getByLabelText("Alternar tema");
    expect(themeButton).toBeInTheDocument();

    await user.hover(themeButton);
    await waitFor(() => {
      expect(screen.getByRole("tooltip", { name: "Alternar tema" })).toBeInTheDocument();
    });

    await user.click(themeButton);
    expect(setThemeMock).toHaveBeenCalled();
  });

  it("renders user avatar in collapsed state", async () => {
    mockSidebar({ state: "collapsed" });
    mockAuth();

    render(<NavUser />);

    const avatarTrigger = screen.getByLabelText("Menu do usuário");
    expect(avatarTrigger).toBeInTheDocument();
    expect(screen.getByText("H")).toBeInTheDocument();
  });

  it("calls logout when clicking exit in dropdown", async () => {
    const logoutMock = vi.fn();
    mockSidebar({ state: "expanded" });
    mockAuth({ logout: logoutMock });

    const user = userEvent.setup();
    render(<NavUser />);

    const menuTrigger = screen.getByLabelText("Menu do usuário");
    await user.click(menuTrigger);

    // Wait for the dropdown content to appear. Radix uses portals.
    const logoutButton = await screen.findByText("Sair");
    await user.click(logoutButton);

    expect(logoutMock).toHaveBeenCalled();
  });

  it("navigates to settings and account from expanded menu", async () => {
    mockSidebar({ state: "expanded" });
    mockAuth();

    const user = userEvent.setup();
    render(<NavUser />);

    const menuTrigger = screen.getByLabelText("Menu do usuário");
    await user.click(menuTrigger);

    const accountButton = await screen.findByText("Minha Conta");
    await user.click(accountButton);
    expect(navigateMock).toHaveBeenCalledWith("/settings");

    // Re-open menu for next interaction
    await user.click(menuTrigger);
    const settingsButton = await screen.findByText("Configurações");
    await user.click(settingsButton);
    expect(navigateMock).toHaveBeenCalledWith("/settings");
  });

  it("toggles theme and navigates from collapsed menu", async () => {
    mockSidebar({ state: "collapsed" });
    mockAuth();

    const user = userEvent.setup();
    render(<NavUser />);

    const menuTrigger = screen.getByLabelText("Menu do usuário");
    await user.click(menuTrigger);

    const themeToggle = await screen.findByText("Modo Escuro");
    await user.click(themeToggle);
    expect(setThemeMock).toHaveBeenCalled();

    // Menu usually closes on click, re-open if needed
    await user.click(menuTrigger);
    const accountButton = await screen.findByText("Minha Conta");
    await user.click(accountButton);
    expect(navigateMock).toHaveBeenCalledWith("/settings");
  });
});
