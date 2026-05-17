import { describe, expect, it } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { FormProvider, useForm } from "react-hook-form";
import { WeddingFormFields } from "./WeddingFormFields";

interface TestFormValues {
  groom_name: string;
  bride_name: string;
  date: string;
  location: string;
  expected_guests?: number | null;
}

function FormWrapper({
  placeholders,
  expectedGuestsLabel,
}: {
  placeholders?: Partial<
    Record<"groom_name" | "bride_name" | "location", string>
  >;
  expectedGuestsLabel?: string;
}) {
  const form = useForm<TestFormValues>({
    defaultValues: {
      groom_name: "",
      bride_name: "",
      date: "",
      location: "",
      expected_guests: undefined,
    },
  });

  return (
    <FormProvider {...form}>
      <WeddingFormFields
        form={form}
        placeholders={placeholders}
        expectedGuestsLabel={expectedGuestsLabel}
      />
    </FormProvider>
  );
}

describe("WeddingFormFields", () => {
  it("renders all five form fields with correct labels", () => {
    render(<FormWrapper />);

    expect(screen.getByLabelText("Nome do Noivo")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome da Noiva")).toBeInTheDocument();
    expect(screen.getByLabelText("Data do Casamento")).toBeInTheDocument();
    expect(screen.getByLabelText("Número de Convidados")).toBeInTheDocument();
    expect(screen.getByLabelText("Local")).toBeInTheDocument();
  });

  it("renders placeholders for groom_name, bride_name, and location", () => {
    render(
      <FormWrapper
        placeholders={{
          groom_name: "João Silva",
          bride_name: "Maria Santos",
          location: "Salão de Festas",
        }}
      />,
    );

    expect(screen.getByPlaceholderText("João Silva")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Maria Santos")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Salão de Festas"),
    ).toBeInTheDocument();
  });

  it("renders date input with type='date'", () => {
    render(<FormWrapper />);

    const dateInput = screen.getByLabelText("Data do Casamento");
    expect(dateInput).toHaveAttribute("type", "date");
  });

  it("renders expected_guests input with type='number'", () => {
    render(<FormWrapper />);

    const guestsInput = screen.getByLabelText("Número de Convidados");
    expect(guestsInput).toHaveAttribute("type", "number");
  });

  it("accepts custom expectedGuestsLabel", () => {
    render(
      <FormWrapper expectedGuestsLabel="Total de Convidados (Opcional)" />,
    );

    expect(
      screen.getByLabelText("Total de Convidados (Opcional)"),
    ).toBeInTheDocument();
    expect(
      screen.queryByLabelText("Número de Convidados"),
    ).not.toBeInTheDocument();
  });

  it("typing in groom_name updates the input value", async () => {
    render(<FormWrapper />);

    const user = userEvent.setup();
    const input = screen.getByLabelText("Nome do Noivo");
    await user.type(input, "José Pereira");

    expect(input).toHaveValue("José Pereira");
  });

  it("typing in bride_name updates the input value", async () => {
    render(<FormWrapper />);

    const user = userEvent.setup();
    const input = screen.getByLabelText("Nome da Noiva");
    await user.type(input, "Ana Clara");

    expect(input).toHaveValue("Ana Clara");
  });

  it("typing in location updates the input value", async () => {
    render(<FormWrapper />);

    const user = userEvent.setup();
    const input = screen.getByLabelText("Local");
    await user.type(input, "Igreja Matriz");

    expect(input).toHaveValue("Igreja Matriz");
  });

  it("typing in date updates the input value", async () => {
    render(<FormWrapper />);

    const user = userEvent.setup();
    const input = screen.getByLabelText("Data do Casamento");
    await user.type(input, "2025-12-25");

    expect(input).toHaveValue("2025-12-25");
  });

  it("typing a number in expected_guests updates the input value", async () => {
    render(<FormWrapper />);

    const user = userEvent.setup();
    const input = screen.getByLabelText("Número de Convidados");
    await user.type(input, "200");

    expect(input).toHaveValue(200);
  });
});
