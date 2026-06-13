import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@/test-utils";
import { GlobalError } from "@/components/ui/globalError";

// We need to mock useRouteError but keep other react-router-dom exports
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return {
    ...actual,
    useRouteError: vi.fn(),
  };
});

import { useRouteError } from "react-router-dom";

const mockError = new Error("Falha na conexão com o servidor");
mockError.stack = "Error: Falha na conexão com o servidor\n  at Component (file.tsx:10:5)\n  at render (file.tsx:20:3)";

describe("GlobalError", () => {
  beforeEach(() => {
    vi.mocked(useRouteError).mockReturnValue(mockError);
  });

  it("renders error title 'Erro Inesperado'", () => {
    render(<GlobalError />);

    expect(
      screen.getByRole("heading", { name: /erro inesperado/i }),
    ).toBeInTheDocument();
  });

  it("renders PT-BR description text", () => {
    render(<GlobalError />);

    expect(
      screen.getByText(
        /algo deu errado ao carregar esta seção/i,
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /verifique sua conexão ou tente novamente/i,
      ),
    ).toBeInTheDocument();
  });

  it("in DEV mode, shows error message", () => {
    render(<GlobalError />);

    expect(
      screen.getByText("Falha na conexão com o servidor"),
    ).toBeInTheDocument();
  });

  it("in DEV mode, shows stack trace", () => {
    render(<GlobalError />);

    const stackTrace = screen.getByText(
      /Error: Falha na conexão com o servidor/,
    );
    expect(stackTrace).toBeInTheDocument();
    expect(stackTrace.tagName).toBe("PRE");
  });

  it("renders 'Voltar ao Início' button", () => {
    render(<GlobalError />);

    const backButton = screen.getByRole("button", {
      name: /voltar ao início/i,
    });
    expect(backButton).toBeInTheDocument();
  });

  it("'Voltar ao Início' button navigates to home", () => {
    render(<GlobalError />);

    const backButton = screen.getByRole("button", {
      name: /voltar ao início/i,
    });
    backButton.click();

    // happy-dom resolves relative URLs to absolute
    expect(window.location.href).toMatch(/\/$/);
  });
});
