export type SupplierFormMode = "create" | "edit";
export type SupplierStatusFilter = "all" | "active" | "inactive";

export interface SupplierFormState {
  uuid?: string;
  name: string;
  cnpj: string;
  phone: string;
  email: string;
  status: Exclude<SupplierStatusFilter, "all">;
}

export const EMPTY_SUPPLIER_FORM_STATE: SupplierFormState = {
  name: "",
  cnpj: "",
  phone: "",
  email: "",
  status: "active",
};
