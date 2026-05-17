import { useState, useEffect, useCallback } from "react";

import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface ContractCreateExpenseFieldsProps {
  categories: { uuid: string; name: string }[];
  onExpenseChange: (values: {
    category: string;
    numInstallments: number;
    firstDueDate: string;
    checked: boolean;
  }) => void;
}

export function ContractCreateExpenseFields({
  categories,
  onExpenseChange,
}: ContractCreateExpenseFieldsProps) {
  const [checked, setChecked] = useState(false);
  const [category, setCategory] = useState("");
  const [numInstallments, setNumInstallments] = useState(1);
  const [firstDueDate, setFirstDueDate] = useState(
    () => new Date().toISOString().slice(0, 10),
  );

  const notify = useCallback(
    (overrides: Partial<Parameters<typeof onExpenseChange>[0]>) => {
      onExpenseChange({
        category,
        numInstallments,
        firstDueDate,
        checked,
        ...overrides,
      });
    },
    [onExpenseChange, category, numInstallments, firstDueDate, checked],
  );

  useEffect(() => {
    notify({});
  }, [notify]);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Checkbox
          id="create-expense"
          checked={checked}
          onCheckedChange={(v) => {
            const newChecked = !!v;
            setChecked(newChecked);
            notify({ checked: newChecked });
          }}
        />
        <label
          htmlFor="create-expense"
          className="text-sm font-medium cursor-pointer"
        >
          Criar despesa a partir deste contrato
        </label>
      </div>

      {checked && (
        <div className="space-y-3 pl-6">
          <div className="space-y-1">
            <label className="text-xs font-medium">Categoria da Despesa</label>
            <Select
              value={category}
              onValueChange={(v) => {
                setCategory(v);
                notify({ category: v });
              }}
            >
              <SelectTrigger className="h-8 text-sm">
                <SelectValue placeholder="Selecione uma categoria" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((c) => (
                  <SelectItem key={c.uuid} value={c.uuid}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium">Nº de Parcelas</label>
              <Input
                type="number"
                min={1}
                value={numInstallments}
                onChange={(e) => {
                  const val = Math.max(1, Number(e.target.value) || 1);
                  setNumInstallments(val);
                  notify({ numInstallments: val });
                }}
                className="h-8 text-sm"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Venc. 1ª Parcela</label>
              <Input
                type="date"
                value={firstDueDate}
                onChange={(e) => {
                  setFirstDueDate(e.target.value);
                  notify({ firstDueDate: e.target.value });
                }}
                className="h-8 text-sm"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
