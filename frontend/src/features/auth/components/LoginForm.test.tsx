import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { server } from "@/mocks/server";
import { getAuthObtainTokenMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";
import type { TokenOut } from "@/api/generated/v1/models/tokenOut";

const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: {
      ...actual.toast,
      success: toastSuccess,
      error: toastError,
    },
  };
});

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("LoginForm", () => {
  it("renders the login form", () => {
    render(<LoginForm />);

    expect(screen.getByText("Wedding Admin")).toBeInTheDocument();
    expect(screen.getByLabelText("E-mail")).toBeInTheDocument();
    expect(screen.getByLabelText("Senha")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /entrar no painel/i }),
    ).toBeInTheDocument();
  });

  it("shows validation errors for empty fields", async () => {
    render(<LoginForm />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /entrar no painel/i }));

    await screen.findByText(/invalid/i);
    expect(
      screen.getByText(/invalid email/i),
    ).toBeInTheDocument();
  });

  it("allows typing email and password", async () => {
    render(<LoginForm />);

    const user = userEvent.setup();
    const emailInput = screen.getByLabelText("E-mail");
    const passwordInput = screen.getByLabelText("Senha");

    await user.type(emailInput, "admin@test.com");
    await user.type(passwordInput, "123456");

    expect(emailInput).toHaveValue("admin@test.com");
    expect(passwordInput).toHaveValue("123456");
  });

  it("submits and navigates on success", async () => {
    const mockToken: TokenOut = {
      access: "access-token-xyz",
      refresh: "refresh-token-xyz",
      user: {
        id: 1,
        first_name: "Admin",
        last_name: "User",
        email: "admin@test.com",
      },
    };
    server.use(
      getAuthObtainTokenMockHandler(mockToken),
    );

    render(<LoginForm />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("E-mail"), "admin@test.com");
    await user.type(screen.getByLabelText("Senha"), "12345678");
    await user.click(screen.getByRole("button", { name: /entrar no painel/i }));

    await waitFor(() => {
      expect(toastSuccess).toHaveBeenCalledWith("Bem-vindo, Admin!");
    });
    expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
  });

  it("shows error toast on login failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/auth/token/", () =>
        HttpResponse.json({ detail: "Invalid credentials" }, { status: 401 }),
      ),
    );

    render(<LoginForm />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("E-mail"), "wrong@test.com");
    await user.type(screen.getByLabelText("Senha"), "wrongpass");
    await user.click(screen.getByRole("button", { name: /entrar no painel/i }));

    await waitFor(() => {
      expect(toastError).toHaveBeenCalled();
    });
  });

  it("disables button during submit", async () => {
    const { http, HttpResponse } = await import("msw");
    let resolvePromise: () => void;
    const deferred = new Promise<void>((resolve) => {
      resolvePromise = resolve;
    });
    server.use(
      http.post("*/api/v1/auth/token/", async () => {
        await deferred;
        return HttpResponse.json({
          access: "at", refresh: "rt",
          user: { id: 1, first_name: "T", last_name: "User", email: "t@t.com" },
        });
      }),
    );

    render(<LoginForm />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("E-mail"), "admin@test.com");
    await user.type(screen.getByLabelText("Senha"), "12345678");
    await user.click(screen.getByRole("button", { name: /entrar no painel/i }));

    await screen.findByText("Validando...");
    resolvePromise!();
  });
});
