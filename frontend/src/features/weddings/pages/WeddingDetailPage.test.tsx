import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@/test-utils";
import WeddingDetailPage from "@/features/weddings/pages/WeddingDetailPage";
import { createMockWedding } from "@/test-data";

// Mock useParams to control the uuid param independently of MemoryRouter
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<
    typeof import("react-router-dom")
  >("react-router-dom");
  return {
    ...actual,
    useParams: vi.fn(),
  };
});

// Mock the Orval hook
vi.mock(
  "@/api/generated/v1/endpoints/weddings/weddings",
  async () => {
    const actual = await vi.importActual<
      typeof import("@/api/generated/v1/endpoints/weddings/weddings")
    >("@/api/generated/v1/endpoints/weddings/weddings");
    return {
      ...actual,
      useWeddingsRead: vi.fn(),
    };
  },
);

import { useParams } from "react-router-dom";
import { useWeddingsRead } from "@/api/generated/v1/endpoints/weddings/weddings";

const mockWedding = createMockWedding({
  bride_name: "Maria",
  groom_name: "João",
});

describe("WeddingDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows 'URL inválida' when uuid is undefined", () => {
    vi.mocked(useParams).mockReturnValue({});
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, { initialEntries: ["/weddings"] });

    expect(screen.getByText("URL inválida")).toBeInTheDocument();
    expect(
      screen.getByText(/nenhum uuid de casamento foi encontrado na url/i),
    ).toBeInTheDocument();
  });

  it("shows 'URL inválida' with back-to-list link", () => {
    vi.mocked(useParams).mockReturnValue({});
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, { initialEntries: ["/weddings"] });

    expect(
      screen.getByRole("link", { name: /voltar para lista/i }),
    ).toBeInTheDocument();
  });

  it("shows loading skeleton when isLoading is true", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("shows error alert on API error", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("Erro de rede"),
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(
      screen.getByText("Erro ao carregar casamento"),
    ).toBeInTheDocument();
    expect(screen.getByText("Erro de rede")).toBeInTheDocument();
  });

  it("shows 'casamento não encontrado' when data loads but wedding is null", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: { data: undefined },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(
      screen.getByText("Casamento não encontrado"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /o casamento solicitado não foi encontrado ou você não tem permissão para acessá-lo/i,
      ),
    ).toBeInTheDocument();
  });

  it("shows wedding detail tabs when data loads", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: { data: mockWedding },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(
      screen.getByRole("link", { name: /voltar para lista/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /geral/i })).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: /finanças/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: /logística/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: /planejamento/i }),
    ).toBeInTheDocument();
  });
});
