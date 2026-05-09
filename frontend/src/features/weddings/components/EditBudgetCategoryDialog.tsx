import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import type { z } from "zod";

import { useFinancesCategoriesUpdate } from "@/api/generated/v1/endpoints/finances/finances";
import { FinancesCategoriesUpdateBody } from "@/api/generated/v1/zod/finances/finances";
import { getApiErrorInfo } from "@/api/error-utils";
import type { BudgetCategoryOut } from "@/api/generated/v1/models/budgetCategoryOut";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Loader2, AlertCircle } from "lucide-react";

type EditCategoryFormData = z.infer<typeof FinancesCategoriesUpdateBody>;

interface EditBudgetCategoryDialogProps {
  category: BudgetCategoryOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function EditBudgetCategoryDialog({
  category,
  open,
  onOpenChange,
  onSuccess,
}: EditBudgetCategoryDialogProps) {
  const { mutate, isPending } = useFinancesCategoriesUpdate();

  const form = useForm<EditCategoryFormData>({
    resolver: zodResolver(FinancesCategoriesUpdateBody),
    defaultValues: {
      name: category.name,
      description: category.description ?? null,
      allocated_budget: parseFloat(category.allocated_budget),
    },
  });

  const handleSubmit = form.handleSubmit((data) => {
    mutate(
      { uuid: category.uuid, data },
      {
        onSuccess: () => {
          toast.success("Categoria atualizada com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Falha ao atualizar categoria.",
          );
          toast.error(message);
        },
      },
    );
  });

  const currentSpent = parseFloat(category.total_spent ?? "0");
  const watchAllocated = useWatch({ control: form.control, name: "allocated_budget" });
  const numericValue =
    watchAllocated !== null && watchAllocated !== undefined
      ? Number(watchAllocated)
      : null;
  const valueBelowSpent = numericValue !== null && numericValue < currentSpent;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Editar Categoria</DialogTitle>
          <DialogDescription>
            Altere o nome ou valor orçado da categoria {category.name}.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Nome da categoria"
                      {...field}
                      value={field.value ?? ""}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="allocated_budget"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Valor Orçado (R$)</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="0,00"
                      {...field}
                      onChange={(e) =>
                        field.onChange(
                          e.target.value === ""
                            ? null
                            : parseFloat(e.target.value),
                        )
                      }
                      value={field.value ?? ""}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descrição (opcional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Detalhes sobre esta categoria..."
                      {...field}
                      value={field.value ?? ""}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {valueBelowSpent && (
              <div className="flex items-start gap-2 p-3 rounded-md bg-amber-50 dark:bg-amber-950/30 text-amber-800 dark:text-amber-200 text-sm">
                <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                <span>
                  O novo valor é menor que o total já gasto (R${" "}
                  {currentSpent.toLocaleString("pt-BR", {
                    minimumFractionDigits: 2,
                  })}
                  ).
                </span>
              </div>
            )}
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={isPending}>
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Salvar
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
