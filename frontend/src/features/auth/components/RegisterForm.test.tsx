import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { RegisterForm } from "@/features/auth/components/RegisterForm";
import { server } from "@/mocks/server";
import { getAuthRegisterUserMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";
import type { UserOut } from "@/api/generated/v1/models/userOut";

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

describe("RegisterForm", () => {
  it("renders the registration form", () => {
    render(<RegisterForm />);

    expect(
      screen.getByRole("heading", { name: /criar conta/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toBeInTheDocument();
    expect(screen.getByLabelText("Sobrenome")).toBeInTheDocument();
    expect(screen.getByLabelText("E-mail")).toBeInTheDocument();
    expect(screen.getByLabelText("Senha")).toBeInTheDocument();
    expect(screen.getByLabelText("Confirmar Senha")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /criar conta/i }),
    ).toBeInTheDocument();
  });

  it("has a link to login page", () => {
    render(<RegisterForm />);

    const loginLink = screen.getByRole("link", { name: /faça login/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute("href", "/login");
  });

  it("shows validation errors for empty fields", async () => {
    render(<RegisterForm />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /criar conta/i }));

    await screen.findByText(/invalid/i);
    expect(
      screen.getByText(/invalid email/i),
    ).toBeInTheDocument();
  });

  it("shows error when passwords do not match", async () => {
    render(<RegisterForm />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Senha"), "12345678");
    await user.type(screen.getByLabelText("Confirmar Senha"), "87654321");
    await user.click(screen.getByRole("button", { name: /criar conta/i }));

    expect(
      await screen.findByText("Senhas não conferem"),
    ).toBeInTheDocument();
  });

  it("allows typing all fields", async () => {
    render(<RegisterForm />);

    const user = userEvent.setup();
    const firstNameInput = screen.getByLabelText("Nome");
    const lastNameInput = screen.getByLabelText("Sobrenome");
    const emailInput = screen.getByLabelText("E-mail");
    const passwordInput = screen.getByLabelText("Senha");
    const confirmInput = screen.getByLabelText("Confirmar Senha");

    await user.type(firstNameInput, "João");
    await user.type(lastNameInput, "Silva");
    await user.type(emailInput, "joao@test.com");
    await user.type(passwordInput, "123456");
    await user.type(confirmInput, "123456");

    expect(firstNameInput).toHaveValue("João");
    expect(lastNameInput).toHaveValue("Silva");
    expect(emailInput).toHaveValue("joao@test.com");
    expect(passwordInput).toHaveValue("123456");
    expect(confirmInput).toHaveValue("123456");
  });

  it("submits and navigates to login on success", async () => {
    const mockUser: UserOut = {
      uuid: "abc-123",
      email: "joao@test.com",
      first_name: "João",
      last_name: "Silva",
      company_slug: "joao-silva",
    };
    server.use(
      getAuthRegisterUserMockHandler(mockUser),
    );

    render(<RegisterForm />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nome"), "João");
    await user.type(screen.getByLabelText("Sobrenome"), "Silva");
    await user.type(screen.getByLabelText("E-mail"), "joao@test.com");
    await user.type(screen.getByLabelText("Senha"), "12345678");
    await user.type(screen.getByLabelText("Confirmar Senha"), "12345678");
    await user.click(screen.getByRole("button", { name: /criar conta/i }));

    await waitFor(() => {
      expect(toastSuccess).toHaveBeenCalledWith(
        "Conta criada com sucesso! Faça login para continuar.",
      );
    });
    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });

  it("shows error toast on registration failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/auth/register/", () =>
        HttpResponse.json(
          { detail: "Este e-mail já está cadastrado em outra conta." },
          { status: 409 },
        ),
      ),
    );

    render(<RegisterForm />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("E-mail"), "existing@test.com");
    await user.type(screen.getByLabelText("Senha"), "12345678");
    await user.type(screen.getByLabelText("Confirmar Senha"), "12345678");
    await user.click(screen.getByRole("button", { name: /criar conta/i }));

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
      http.post("*/api/v1/auth/register/", async () => {
        await deferred;
        return HttpResponse.json({
          uuid: "abc-123",
          email: "joao@test.com",
          first_name: "João",
          last_name: "Silva",
          company_slug: "joao-silva",
        });
      }),
    );

    render(<RegisterForm />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nome"), "João");
    await user.type(screen.getByLabelText("E-mail"), "joao@test.com");
    await user.type(screen.getByLabelText("Senha"), "12345678");
    await user.type(screen.getByLabelText("Confirmar Senha"), "12345678");
    await user.click(screen.getByRole("button", { name: /criar conta/i }));

    await screen.findByText("Criando conta...");
    resolvePromise!();
  });
});
