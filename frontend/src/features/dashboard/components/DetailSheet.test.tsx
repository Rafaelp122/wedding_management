import { describe, expect, it } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { DetailSheet } from "./DetailSheet";
import { Clock } from "lucide-react";

describe("DetailSheet", () => {
  it("opens and shows loading state", async () => {
    const user = userEvent.setup();
    render(
      <DetailSheet
        trigger={<button>Ver detalhes</button>}
        title="Detalhes"
        description="Descrição detalhada"
        icon={Clock}
        iconColor="text-blue-500"
        isLoading
        isEmpty={false}
        emptyMessage="Vazio"
      >
        <div>Conteúdo</div>
      </DetailSheet>,
    );

    await user.click(screen.getByText("Ver detalhes"));

    expect(screen.getByText("Detalhes")).toBeInTheDocument();
    expect(screen.getByText("Descrição detalhada")).toBeInTheDocument();
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("opens and shows empty state", async () => {
    const user = userEvent.setup();
    render(
      <DetailSheet
        trigger={<button>Ver detalhes</button>}
        title="Detalhes"
        description="Descrição"
        icon={Clock}
        iconColor="text-blue-500"
        isLoading={false}
        isEmpty
        emptyMessage="Nenhum item encontrado"
      >
        <div>Conteúdo</div>
      </DetailSheet>,
    );

    await user.click(screen.getByText("Ver detalhes"));

    expect(screen.getByText("Nenhum item encontrado")).toBeInTheDocument();
  });

  it("opens and shows children when populated", async () => {
    const user = userEvent.setup();
    render(
      <DetailSheet
        trigger={<button>Ver detalhes</button>}
        title="Detalhes"
        description="Descrição"
        icon={Clock}
        iconColor="text-blue-500"
        isLoading={false}
        isEmpty={false}
        emptyMessage="Vazio"
      >
        <div data-testid="content">Conteúdo do sheet</div>
      </DetailSheet>,
    );

    await user.click(screen.getByText("Ver detalhes"));

    expect(screen.getByTestId("content")).toBeInTheDocument();
    expect(screen.getByText("Conteúdo do sheet")).toBeInTheDocument();
  });
});
