import { describe, expect, it } from "vitest";
import {
  getSupplierFormValidationMessage,
  buildSupplierPayload,
} from "@/features/logistics/utils/supplierForm";
import type { SupplierFormState } from "@/features/logistics/types";

const completeState: SupplierFormState = {
  name: "Fornecedor X",
  cnpj: "12.345.678/0001-90",
  phone: "(11) 99999-0000",
  email: "fornecedor@email.com",
  status: "active",
};

describe("getSupplierFormValidationMessage", () => {
  it("returns null when all fields are filled", () => {
    expect(getSupplierFormValidationMessage(completeState)).toBeNull();
  });

  it("returns message for empty name", () => {
    expect(
      getSupplierFormValidationMessage({ ...completeState, name: "  " }),
    ).toBe("Informe o nome do fornecedor.");
  });

  it("returns message for empty email", () => {
    expect(
      getSupplierFormValidationMessage({ ...completeState, email: "" }),
    ).toBe("Informe o e-mail do fornecedor.");
  });

  it("returns message for empty phone", () => {
    expect(
      getSupplierFormValidationMessage({ ...completeState, phone: "" }),
    ).toBe("Informe o telefone do fornecedor.");
  });

  it("returns message for empty cnpj", () => {
    expect(
      getSupplierFormValidationMessage({ ...completeState, cnpj: "" }),
    ).toBe("Informe o CNPJ do fornecedor.");
  });

  it("checks name first", () => {
    expect(
      getSupplierFormValidationMessage({
        ...completeState,
        name: "",
        email: "",
      }),
    ).toBe("Informe o nome do fornecedor.");
  });
});

describe("buildSupplierPayload", () => {
  it("builds payload with trimmed values", () => {
    const payload = buildSupplierPayload({
      ...completeState,
      name: "  Fornecedor  ",
    });
    expect(payload).toEqual({
      name: "Fornecedor",
      cnpj: "12.345.678/0001-90",
      phone: "(11) 99999-0000",
      email: "fornecedor@email.com",
      is_active: true,
    });
  });

  it("maps active status to is_active true", () => {
    const payload = buildSupplierPayload(completeState);
    expect(payload.is_active).toBe(true);
  });

  it("maps inactive status to is_active false", () => {
    const payload = buildSupplierPayload({
      ...completeState,
      status: "inactive",
    });
    expect(payload.is_active).toBe(false);
  });
});
