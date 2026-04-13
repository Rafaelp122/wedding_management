import { AlertCircle, Receipt } from "lucide-react";

import { useWeddingExpenses } from "../hooks/useWeddingExpenses";
import { WeddingExpensesTable } from "./WeddingExpensesTable";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface WeddingExpensesTabProps {
  weddingUuid: string;
}

export function WeddingExpensesTab({ weddingUuid }: WeddingExpensesTabProps) {
  const { expenses, isLoading, error } = useWeddingExpenses(weddingUuid);

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-[300px] w-full rounded-md" />
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
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Receipt className="size-5 text-primary" />
            Despesas Registradas
          </CardTitle>
          <CardDescription>
            Acompanhamento detalhado das despesas vinculadas às categorias orçamentárias.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <WeddingExpensesTable expenses={expenses} />
        </CardContent>
      </Card>
    </div>
  );
}
