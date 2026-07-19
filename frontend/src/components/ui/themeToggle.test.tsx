import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ThemeToggle } from "./themeToggle";

// Setup localStorage Mock
const localStorageStore: Record<string, string> = {};
const mockGetItem = vi.fn((key: string) => localStorageStore[key] || null);
const mockSetItem = vi.fn((key: string, value: string) => {
  localStorageStore[key] = value;
});

Object.defineProperty(window, "localStorage", {
  value: {
    getItem: mockGetItem,
    setItem: mockSetItem,
  },
  writable: true,
});

// Mock next-themes useTheme while preserving ThemeProvider
const mockSetTheme = vi.fn();
let currentTheme = "light";

vi.mock("next-themes", async (importOriginal) => {
  const actual = await importOriginal<typeof import("next-themes")>();
  return {
    ...actual,
    useTheme: () => ({
      theme: currentTheme,
      setTheme: (theme: string) => {
        currentTheme = theme;
        window.localStorage.setItem("theme", theme);
        mockSetTheme(theme);
      },
      themes: ["light", "dark"],
    }),
  };
});

describe("ThemeToggle", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    currentTheme = "light";
    delete localStorageStore["theme"];
  });

  it("should render the toggle button with correct aria-label", () => {
    render(<ThemeToggle />);
    const button = screen.getByRole("button", { name: "Alternar tema" });
    expect(button).toBeInTheDocument();
  });

  it("should switch theme from light to dark on click and write to localStorage", async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByRole("button", { name: "Alternar tema" });

    // Initial state is light, clicking should toggle to dark
    await user.click(button);

    expect(mockSetTheme).toHaveBeenCalledWith("dark");
    expect(mockSetItem).toHaveBeenCalledWith("theme", "dark");
    expect(currentTheme).toBe("dark");
  });

  it("should switch theme from dark to light on click if current theme is dark", async () => {
    currentTheme = "dark";
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByRole("button", { name: "Alternar tema" });

    await user.click(button);

    expect(mockSetTheme).toHaveBeenCalledWith("light");
    expect(mockSetItem).toHaveBeenCalledWith("theme", "light");
    expect(currentTheme).toBe("light");
  });
});
