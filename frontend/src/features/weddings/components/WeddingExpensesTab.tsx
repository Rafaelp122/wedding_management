import { useState } from "react";
import { AlertCircle, Receipt, Plus } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import { useWeddingExpenses } from "../hooks/useWeddingExpenses";
import { WeddingExpensesTable } from "./WeddingExpensesTable";
import { CreateExpenseDialog } from "./CreateExpenseDialog";

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

interface WeddingExpensesTabProps {
  weddingUuid: string;
}

export function WeddingExpensesTab({ weddingUuid }: WeddingExpensesTabProps) {
  const { expenses, isLoading, error } = useWeddingExpenses(weddingUuid);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  const handleRefresh = () => {
    queryClient.invalidateQueries();
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
            weddingUuid={weddingUuid}
            onExpenseUpdated={handleRefresh}
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
    </div>
  );
}
