import { describe, expect, it } from "vitest";
import { SupplierFormSchema } from "./supplierFormSchema";

describe("SupplierFormSchema", () => {
  const validSupplier = {
    name: "Fornecedor Teste",
    cnpj: "12.345.678/0001-90",
    phone: "11999999999",
    email: "teste@fornecedor.com",
    address: "Rua Teste, 123",
    city: "São Paulo",
    state: "SP",
    website: "https://fornecedor.com",
    notes: "Observações do fornecedor",
  };

  it("should validate a completely valid supplier payload", () => {
    const result = SupplierFormSchema.safeParse(validSupplier);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.cnpj).toBe(validSupplier.cnpj);
    }
  });

  it("should fail validation if CNPJ is in the wrong format", () => {
    const invalidSupplier = {
      ...validSupplier,
      cnpj: "12345678000190", // missing formatting dots, slash, dash
    };
    const result = SupplierFormSchema.safeParse(invalidSupplier);
    expect(result.success).toBe(false);
    if (!result.success) {
      const issue = result.error.issues.find((i) => i.path.includes("cnpj"));
      expect(issue).toBeDefined();
      expect(issue?.message).toBe("CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX.");
    }
  });

  it("should fail validation if required fields are missing", () => {
    const invalidSupplier = {
      cnpj: "12.345.678/0001-90",
    };
    const result = SupplierFormSchema.safeParse(invalidSupplier);
    expect(result.success).toBe(false);
    if (!result.success) {
      const paths = result.error.issues.map((i) => i.path.join("."));
      expect(paths).toContain("name");
      expect(paths).toContain("phone");
      expect(paths).toContain("email");
    }
  });

  it("should fail validation if state is invalid", () => {
    const invalidSupplier = {
      ...validSupplier,
      state: "SPP", // must be 2 uppercase chars or empty
    };
    const result = SupplierFormSchema.safeParse(invalidSupplier);
    expect(result.success).toBe(false);
  });

  it("should fail validation if website format is invalid", () => {
    const invalidSupplier = {
      ...validSupplier,
      website: "invalid-url",
    };
    const result = SupplierFormSchema.safeParse(invalidSupplier);
    expect(result.success).toBe(false);
  });
});
