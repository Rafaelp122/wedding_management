import { lazy, Suspense, useState } from "react";
import { AlertCircle, Receipt, Plus } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";
import { useWeddingExpenses } from "../../hooks/useExpenses";
import { WeddingExpensesTable } from "./ExpensesTable";
import { CreateExpenseDialog } from "./CreateExpenseDialog";
import { getFinancesExpensesListQueryKey } from "@/api/generated/v1/endpoints/finances/finances";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const EditExpenseDialog = lazy(
  () => import("./EditExpenseDialog").then((m) => ({ default: m.EditExpenseDialog })),
);
const DeleteExpenseDialog = lazy(
  () => import("./DeleteExpenseDialog").then((m) => ({ default: m.DeleteExpenseDialog })),
);
const ExpenseDetailSheet = lazy(
  () => import("./ExpenseDetailSheet").then((m) => ({ default: m.ExpenseDetailSheet })),
);

interface WeddingExpensesTabProps {
  weddingUuid: string;
}

export function WeddingExpensesTab({ weddingUuid }: WeddingExpensesTabProps) {
  const { expenses, isLoading, error } = useWeddingExpenses(weddingUuid);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<ExpenseOut | null>(null);
  const [deletingExpense, setDeletingExpense] = useState<ExpenseOut | null>(null);
  const [detailExpense, setDetailExpense] = useState<ExpenseOut | null>(null);
  const queryClient = useQueryClient();

  const handleRefresh = () => {
    queryClient.invalidateQueries({
      queryKey: getFinancesExpensesListQueryKey({ wedding_id: weddingUuid }),
    });
  };

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-75 w-full rounded-md" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="size-4" />
        <AlertDescription>
          Não foi possível carregar as despesas deste casamento.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Receipt className="size-5 text-primary" />
              Despesas Registradas
            </CardTitle>
            <CardDescription>
              Acompanhamento detalhado das despesas vinculadas às categorias
              orçamentárias.
            </CardDescription>
          </div>
          <Button
            size="sm"
            onClick={() => setCreateDialogOpen(true)}
            className="gap-2"
          >
            <Plus className="size-4" />
            Nova Despesa
          </Button>
        </CardHeader>
        <CardContent>
          <WeddingExpensesTable
            expenses={expenses}
            onEditExpense={setEditingExpense}
            onDeleteExpense={setDeletingExpense}
            onDetailExpense={setDetailExpense}
          />
        </CardContent>
      </Card>

      <CreateExpenseDialog
        weddingUuid={weddingUuid}
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSuccess={() => {
          setCreateDialogOpen(false);
          handleRefresh();
        }}
      />

      {editingExpense ? (
        <Suspense fallback={null}>
          <EditExpenseDialog
            expense={editingExpense}
            weddingUuid={weddingUuid}
            open={!!editingExpense}
            onOpenChange={(open) => {
              if (!open) setEditingExpense(null);
            }}
            onSuccess={() => {
              setEditingExpense(null);
              handleRefresh();
            }}
          />
        </Suspense>
      ) : null}

      {deletingExpense ? (
        <Suspense fallback={null}>
          <DeleteExpenseDialog
            expense={deletingExpense}
            open={!!deletingExpense}
            onOpenChange={(open) => {
              if (!open) setDeletingExpense(null);
            }}
            onSuccess={() => {
              setDeletingExpense(null);
              handleRefresh();
            }}
          />
        </Suspense>
      ) : null}

      {detailExpense ? (
        <Suspense fallback={null}>
          <ExpenseDetailSheet
            expense={detailExpense}
            open={!!detailExpense}
            onOpenChange={(open) => {
              if (!open) setDetailExpense(null);
            }}
          />
        </Suspense>
      ) : null}
    </div>
  );
}
