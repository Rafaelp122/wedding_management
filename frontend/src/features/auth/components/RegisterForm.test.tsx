import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { RegisterForm } from "@/features/auth/components/RegisterForm";
import { server } from "@/mocks/server";
import { getAuthRegisterUserMockHandler } from "@/api/generated/v1/endpoints/auth/auth.msw";
import type { UserOut } from "@/api/generated/v1/models/userOut";
import { toast } from "sonner";

const mockNavigate = vi.hoisted(() => vi.fn());
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

    expect(screen.getByText("Comece o seu teste")).toBeInTheDocument();
    expect(screen.getByText("Nome")).toBeInTheDocument();
    expect(screen.getByText("Sobrenome")).toBeInTheDocument();
    expect(screen.getByText("E-mail de Trabalho")).toBeInTheDocument();
    expect(
      screen.getByText("Nome da sua Assessoria / Agência"),
    ).toBeInTheDocument();
    expect(screen.getByText("Confirmar Senha")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /criar minha conta agora/i }),
    ).toBeInTheDocument();
  });

  it("has a link to login page", () => {
    render(<RegisterForm />);

    const loginLink = screen.getByRole("link", { name: /acessar painel/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute("href", "/login");
  });

  it("shows validation errors for empty fields", async () => {
    render(<RegisterForm />);

    const user = userEvent.setup();
    await user.click(
      screen.getByRole("button", { name: /criar minha conta agora/i }),
    );

    await screen.findByText(/invalid email/i);
  });

  it("shows error when passwords do not match", async () => {
    render(<RegisterForm />);

    const user = userEvent.setup();
    await user.type(screen.getByPlaceholderText("Helena"), "Helena");
    await user.type(screen.getByPlaceholderText("Costa"), "Costa");
    await user.type(
      screen.getByPlaceholderText("nome@agencia.com"),
      "teste@test.com",
    );
    const passwordInputs = screen.getAllByPlaceholderText("••••••••");
    await user.type(passwordInputs[0], "12345678");
    await user.type(passwordInputs[1], "87654321");
    await user.click(screen.getByRole("checkbox"));
    await user.click(
      screen.getByRole("button", { name: /criar minha conta agora/i }),
    );

    expect(await screen.findByText("Senhas não conferem")).toBeInTheDocument();
  });

  it("allows typing all fields", async () => {
    render(<RegisterForm />);

    const user = userEvent.setup();
    const firstName = screen.getByPlaceholderText("Helena");
    const lastName = screen.getByPlaceholderText("Costa");
    const agency = screen.getByPlaceholderText("Sua Assessoria de Eventos");
    const email = screen.getByPlaceholderText("nome@agencia.com");
    const passwordInputs = screen.getAllByPlaceholderText("••••••••");

    await user.type(firstName, "Helena");
    await user.type(lastName, "Costa");
    await user.type(agency, "Aura Eventos");
    await user.type(email, "helena@simaceito.com");
    await user.type(passwordInputs[0], "12345678");
    await user.type(passwordInputs[1], "12345678");

    expect(firstName).toHaveValue("Helena");
    expect(lastName).toHaveValue("Costa");
    expect(agency).toHaveValue("Aura Eventos");
    expect(email).toHaveValue("helena@simaceito.com");
    expect(passwordInputs[0]).toHaveValue("12345678");
    expect(passwordInputs[1]).toHaveValue("12345678");
  });

  it("submits and navigates to login on success", async () => {
    const mockUser: UserOut = {
      uuid: "abc-123",
      email: "joao@test.com",
      first_name: "João",
      last_name: "Silva",
      company_slug: "joao-silva",
    };
    server.use(getAuthRegisterUserMockHandler(mockUser));

    render(<RegisterForm />);

    const user = userEvent.setup();
    await user.type(screen.getByPlaceholderText("Helena"), "João");
    await user.type(screen.getByPlaceholderText("Costa"), "Silva");
    await user.type(
      screen.getByPlaceholderText("Sua Assessoria de Eventos"),
      "Silva Eventos",
    );
    await user.type(
      screen.getByPlaceholderText("nome@agencia.com"),
      "joao@test.com",
    );
    const passwordInputs = screen.getAllByPlaceholderText("••••••••");
    await user.type(passwordInputs[0], "12345678");
    await user.type(passwordInputs[1], "12345678");
    await user.click(screen.getByRole("checkbox"));
    await user.click(
      screen.getByRole("button", { name: /criar minha conta agora/i }),
    );

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Conta criada com sucesso! Faça login para continuar.",
      );
      expect(mockNavigate).toHaveBeenCalledWith("/login");
    });
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
    await user.type(
      screen.getByPlaceholderText("nome@agencia.com"),
      "existing@test.com",
    );
    const passwordInputs = screen.getAllByPlaceholderText("••••••••");
    await user.type(passwordInputs[0], "12345678");
    await user.type(passwordInputs[1], "12345678");
    await user.click(screen.getByRole("checkbox"));
    await user.click(
      screen.getByRole("button", { name: /criar minha conta agora/i }),
    );

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
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
    await user.type(screen.getByPlaceholderText("Helena"), "João");
    await user.type(
      screen.getByPlaceholderText("nome@agencia.com"),
      "joao@test.com",
    );
    const passwordInputs = screen.getAllByPlaceholderText("••••••••");
    await user.type(passwordInputs[0], "12345678");
    await user.type(passwordInputs[1], "12345678");
    await user.click(screen.getByRole("checkbox"));
    await user.click(
      screen.getByRole("button", { name: /criar minha conta agora/i }),
    );

    await screen.findByText("Criando sua agência...");
    resolvePromise!();
  });
});
