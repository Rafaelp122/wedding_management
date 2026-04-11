import type { Dispatch, SetStateAction } from "react";

import type { SupplierFormMode, SupplierFormState } from "../types";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface SupplierFormDialogProps {
  open: boolean;
  mode: SupplierFormMode;
  formState: SupplierFormState;
  setFormState: Dispatch<SetStateAction<SupplierFormState>>;
  isSaving: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: () => void;
}

export function SupplierFormDialog({
  open,
  mode,
  formState,
  setFormState,
  isSaving,
  onOpenChange,
  onSave,
}: SupplierFormDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {mode === "create" ? "Novo fornecedor" : "Editar fornecedor"}
          </DialogTitle>
          <DialogDescription>
            Preencha os dados principais para manter o cadastro de fornecedores.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="supplier-name">Nome</Label>
            <Input
              id="supplier-name"
              value={formState.name}
              onChange={(event) =>
                setFormState((current) => ({
                  ...current,
                  name: event.target.value,
                }))
              }
              placeholder="Nome do fornecedor"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="supplier-email">E-mail</Label>
              <Input
                id="supplier-email"
                type="email"
                value={formState.email}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    email: event.target.value,
                  }))
                }
                placeholder="contato@fornecedor.com"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="supplier-phone">Telefone</Label>
              <Input
                id="supplier-phone"
                value={formState.phone}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    phone: event.target.value,
                  }))
                }
                placeholder="(21) 99999-9999"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="supplier-cnpj">CNPJ</Label>
              <Input
                id="supplier-cnpj"
                value={formState.cnpj}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    cnpj: event.target.value,
                  }))
                }
                placeholder="00.000.000/0000-00"
              />
            </div>

            <div className="space-y-2">
              <Label>Status</Label>
              <Select
                value={formState.status}
                onValueChange={(value: "active" | "inactive") =>
                  setFormState((current) => ({
                    ...current,
                    status: value,
                  }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Ativo</SelectItem>
                  <SelectItem value="inactive">Inativo</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button onClick={onSave} disabled={isSaving}>
            {isSaving ? "Salvando..." : "Salvar"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
