import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { FormDialog } from "@/components/form-dialog";
import { useForm } from "react-hook-form";
import { type ReactNode } from "react";

function TestFormDialogWrapper({
  description,
  title = "Teste de FormDialog",
  onSubmit = vi.fn(),
  onOpenChange = vi.fn(),
  children = <div>Campos de teste</div>,
}: {
  description?: string;
  title?: string;
  onSubmit?: () => void;
  onOpenChange?: (open: boolean) => void;
  children?: ReactNode;
}) {
  const form = useForm({
    defaultValues: {
      testField: "",
    },
  });

  return (
    <FormDialog
      open={true}
      onOpenChange={onOpenChange}
      title={title}
      description={description}
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={false}
      submitLabel="Enviar"
    >
      {children}
    </FormDialog>
  );
}

describe("FormDialog", () => {
  it("renders with a provided description", () => {
    render(<TestFormDialogWrapper description="Esta é uma descrição de teste" />);

    expect(
      screen.getByRole("heading", { name: /teste de formdialog/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Esta é uma descrição de teste"),
    ).toBeInTheDocument();
    expect(screen.getByText("Campos de teste")).toBeInTheDocument();
  });

  it("renders with a fallback description when description is omitted", () => {
    render(<TestFormDialogWrapper title="Teste Sem Descricao" />);

    expect(
      screen.getByRole("heading", { name: /teste sem descricao/i }),
    ).toBeInTheDocument();

    const fallbackDesc = screen.getByText("Formulário para teste sem descricao");
    expect(fallbackDesc).toBeInTheDocument();
    expect(fallbackDesc).toHaveClass("sr-only");
  });

  it("calls onOpenChange with false when cancel is clicked", async () => {
    const onOpenChange = vi.fn();
    const user = userEvent.setup();

    render(<TestFormDialogWrapper onOpenChange={onOpenChange} />);

    await user.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
