import type { SupplierFormState } from "../types";

interface SupplierPayload {
  name: string;
  cnpj: string;
  phone: string;
  email: string;
  is_active: boolean;
}

export function getSupplierFormValidationMessage(
  formState: SupplierFormState,
): string | null {
  if (!formState.name.trim()) {
    return "Informe o nome do fornecedor.";
  }

  if (!formState.email.trim()) {
    return "Informe o e-mail do fornecedor.";
  }

  if (!formState.phone.trim()) {
    return "Informe o telefone do fornecedor.";
  }

  if (!formState.cnpj.trim()) {
    return "Informe o CNPJ do fornecedor.";
  }

  return null;
}

export function buildSupplierPayload(formState: SupplierFormState): SupplierPayload {
  return {
    name: formState.name.trim(),
    cnpj: formState.cnpj.trim(),
    phone: formState.phone.trim(),
    email: formState.email.trim(),
    is_active: formState.status === "active",
  };
}
