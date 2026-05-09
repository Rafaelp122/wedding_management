import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import type { z } from "zod";

import {
  useFinancesCategoriesCreate,
  useFinancesBudgetsForWedding,
} from "@/api/generated/v1/endpoints/finances/finances";
import { FinancesCategoriesCreateBody } from "@/api/generated/v1/zod/finances/finances";
import { getApiErrorInfo } from "@/api/error-utils";

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
import { Loader2 } from "lucide-react";

type CreateCategoryFormData = z.infer<typeof FinancesCategoriesCreateBody>;

interface CreateBudgetCategoryDialogProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CreateBudgetCategoryDialog({
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: CreateBudgetCategoryDialogProps) {
  const { mutate, isPending } = useFinancesCategoriesCreate();
  const { data: budgetResponse } = useFinancesBudgetsForWedding(weddingUuid, {
    query: { enabled: open },
  });
  const budget = budgetResponse?.data;

  const form = useForm<CreateCategoryFormData>({
    resolver: zodResolver(FinancesCategoriesCreateBody),
    defaultValues: {
      budget: "",
      name: "",
      description: null,
      allocated_budget: undefined,
    },
  });

  useEffect(() => {
    if (budget?.uuid) {
      form.setValue("budget", budget.uuid);
    }
  }, [budget?.uuid, form]);

  const handleSubmit = form.handleSubmit((data) => {
    mutate(
      { data },
      {
        onSuccess: () => {
          toast.success("Categoria criada com sucesso!");
          form.reset();
          onOpenChange(false);
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Falha ao criar categoria.",
          );
          toast.error(message);
        },
      },
    );
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Nova Categoria</DialogTitle>
          <DialogDescription>
            Adicione um novo grupo de custos ao orçamento.
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
                      placeholder="Ex: Buffet, Decoração..."
                      {...field}
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
                            ? undefined
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
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={isPending || !budget}>
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Criar Categoria
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
