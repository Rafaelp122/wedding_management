import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { useForm, type Control } from "react-hook-form";
import { Form } from "@/components/ui/form";
import {
  FormInput,
  FormNumber,
  FormCurrency,
  FormTextarea,
  FormSelect,
  FormSelectNullable,
} from "./form-fields";
import React from "react";

interface TestFormValues {
  name: string;
  age: number | null | undefined;
  price: number;
  description: string;
  category: string;
  assignedTo: string | null;
}

function TestForm({
  onSubmit,
  defaultValues = {},
  children,
}: {
  onSubmit: (values: TestFormValues) => void;
  defaultValues?: Partial<TestFormValues>;
  children: (control: Control<TestFormValues>) => React.ReactNode;
}) {
  const methods = useForm<TestFormValues>({
    defaultValues: {
      name: "",
      age: undefined,
      price: 0,
      description: "",
      category: "",
      assignedTo: null,
      ...defaultValues,
    },
  });

  return (
    <Form {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        {children(methods.control)}
        <button type="submit">Enviar</button>
      </form>
    </Form>
  );
}

describe("Form Fields Components", () => {
  describe("FormInput", () => {
    it("renders label and placeholder, and handles text input", async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <TestForm onSubmit={onSubmit}>
          {(control) => (
            <FormInput
              control={control}
              name="name"
              label="Nome do Evento"
              placeholder="Digite o nome"
            />
          )}
        </TestForm>
      );

      const label = screen.getByText("Nome do Evento");
      expect(label).toBeInTheDocument();

      const input = screen.getByPlaceholderText("Digite o nome");
      expect(input).toBeInTheDocument();
      expect(input).toHaveValue("");

      await user.type(input, "Casamento de Alice");
      expect(input).toHaveValue("Casamento de Alice");

      const submitButton = screen.getByRole("button", { name: "Enviar" });
      await user.click(submitButton);

      const lastCallData = onSubmit.mock.calls[onSubmit.mock.calls.length - 1][0];
      expect(lastCallData.name).toBe("Casamento de Alice");
    });
  });

  describe("FormNumber", () => {
    it("renders and parses numeric input", async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <TestForm onSubmit={onSubmit} defaultValues={{ age: 25 }}>
          {(control) => (
            <FormNumber
              control={control}
              name="age"
              label="Idade"
              placeholder="Digite a idade"
            />
          )}
        </TestForm>
      );

      const input = screen.getByPlaceholderText("Digite a idade");
      expect(input).toHaveValue(25);

      (input as HTMLInputElement).value = "";
      await user.clear(input);
      await user.type(input, "30");
      expect(input).toHaveValue(30);

      const submitButton = screen.getByRole("button", { name: "Enviar" });
      await user.click(submitButton);

      const lastCallData = onSubmit.mock.calls[onSubmit.mock.calls.length - 1][0];
      expect(lastCallData.age).toBe(30);
    });

    it("converts empty value to transformEmptyTo prop", async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <TestForm onSubmit={onSubmit} defaultValues={{ age: 25 }}>
          {(control) => (
            <FormNumber
              control={control}
              name="age"
              label="Idade"
              transformEmptyTo={null}
            />
          )}
        </TestForm>
      );

      const input = screen.getByLabelText("Idade") as HTMLInputElement;
      input.value = "5";
      await user.type(input, "{backspace}");
      expect(input).toHaveValue(null);

      const submitButton = screen.getByRole("button", { name: "Enviar" });
      await user.click(submitButton);

      const lastCallData = onSubmit.mock.calls[onSubmit.mock.calls.length - 1][0];
      expect(lastCallData.age).toBeNull();
    });

    it("triggers onFocus callback", async () => {
      const onFocus = vi.fn();
      const user = userEvent.setup();

      render(
        <TestForm onSubmit={vi.fn()}>
          {(control) => (
            <FormNumber
              control={control}
              name="age"
              label="Idade"
              onFocus={onFocus}
            />
          )}
        </TestForm>
      );

      const input = screen.getByLabelText("Idade");
      await user.click(input);

      expect(onFocus).toHaveBeenCalledTimes(1);
    });
  });

  describe("FormCurrency", () => {
    it("renders and works as a currency form input", async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <TestForm onSubmit={onSubmit} defaultValues={{ price: 1500.5 }}>
          {(control) => (
            <FormCurrency
              control={control}
              name="price"
              label="Orçamento"
            />
          )}
        </TestForm>
      );

      const input = screen.getByLabelText("Orçamento");
      expect(input).toHaveValue(1500.5);

      (input as HTMLInputElement).value = "";
      await user.clear(input);
      await user.type(input, "2000.75");
      expect(input).toHaveValue(2000.75);

      const submitButton = screen.getByRole("button", { name: "Enviar" });
      await user.click(submitButton);

      const lastCallData = onSubmit.mock.calls[onSubmit.mock.calls.length - 1][0];
      expect(lastCallData.price).toBe(2000.75);
    });
  });

  describe("FormTextarea", () => {
    it("renders textarea and supports value editing", async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <TestForm onSubmit={onSubmit}>
          {(control) => (
            <FormTextarea
              control={control}
              name="description"
              label="Descrição"
              placeholder="Digite detalhes"
            />
          )}
        </TestForm>
      );

      const textarea = screen.getByPlaceholderText("Digite detalhes");
      expect(textarea).toBeInTheDocument();
      expect(textarea).toHaveValue("");

      await user.type(textarea, "Linha 1\nLinha 2");
      expect(textarea).toHaveValue("Linha 1\nLinha 2");

      const submitButton = screen.getByRole("button", { name: "Enviar" });
      await user.click(submitButton);

      const lastCallData = onSubmit.mock.calls[onSubmit.mock.calls.length - 1][0];
      expect(lastCallData.description).toBe("Linha 1\nLinha 2");
    });
  });

  describe("FormSelect", () => {
    const items = [
      { id: "1", label: "Opção A" },
      { id: "2", label: "Opção B" },
    ];

    it("renders and updates form state on select change", async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <TestForm onSubmit={onSubmit}>
          {(control) => (
            <FormSelect
              control={control}
              name="category"
              label="Categoria"
              items={items}
              getItemKey={(item) => item.id}
              getItemLabel={(item) => item.label}
              placeholder="Escolha uma"
            />
          )}
        </TestForm>
      );

      const trigger = screen.getByRole("combobox");
      expect(trigger).toBeInTheDocument();

      // Clique para abrir
      await user.click(trigger);

      // Encontrar a opção na tela e clicar
      const option = screen.getByRole("option", { name: "Opção B" });
      await user.click(option);

      const submitButton = screen.getByRole("button", { name: "Enviar" });
      await user.click(submitButton);

      const lastCallData = onSubmit.mock.calls[onSubmit.mock.calls.length - 1][0];
      expect(lastCallData.category).toBe("2");
    });
  });

  describe("FormSelectNullable", () => {
    const items = [
      { id: "user-a", name: "Rafael" },
      { id: "user-b", name: "Ana" },
    ];

    it("converts select value none to null", async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <TestForm onSubmit={onSubmit} defaultValues={{ assignedTo: "user-a" }}>
          {(control) => (
            <FormSelectNullable
              control={control}
              name="assignedTo"
              label="Responsável"
              items={items}
              getItemKey={(item) => item.id}
              getItemLabel={(item) => item.name}
              noneLabel="Ninguém"
            />
          )}
        </TestForm>
      );

      const trigger = screen.getByRole("combobox");
      expect(trigger).toBeInTheDocument();

      // Clique para abrir
      await user.click(trigger);

      // Clique na opção de "Ninguém"
      const noneOption = screen.getByRole("option", { name: "Ninguém" });
      await user.click(noneOption);

      const submitButton = screen.getByRole("button", { name: "Enviar" });
      await user.click(submitButton);

      const lastCallData = onSubmit.mock.calls[onSubmit.mock.calls.length - 1][0];
      expect(lastCallData.assignedTo).toBeNull();
    });

    it("selects normal options correctly", async () => {
      const onSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <TestForm onSubmit={onSubmit} defaultValues={{ assignedTo: null }}>
          {(control) => (
            <FormSelectNullable
              control={control}
              name="assignedTo"
              label="Responsável"
              items={items}
              getItemKey={(item) => item.id}
              getItemLabel={(item) => item.name}
              noneLabel="Ninguém"
            />
          )}
        </TestForm>
      );

      const trigger = screen.getByRole("combobox");
      await user.click(trigger);

      const option = screen.getByRole("option", { name: "Ana" });
      await user.click(option);

      const submitButton = screen.getByRole("button", { name: "Enviar" });
      await user.click(submitButton);

      const lastCallData = onSubmit.mock.calls[onSubmit.mock.calls.length - 1][0];
      expect(lastCallData.assignedTo).toBe("user-b");
    });
  });
});
