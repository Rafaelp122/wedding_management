import { AlertCircle, ListChecks } from "lucide-react";

import { useWeddingChecklist } from "../hooks/useWeddingChecklist";
import { WeddingChecklistTable } from "./WeddingChecklistTable";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface WeddingChecklistTabProps {
  weddingUuid: string;
}

export function WeddingChecklistTab({ weddingUuid }: WeddingChecklistTabProps) {
  const { tasks, isLoading, error, isUpdating, toggleTaskCompletion } =
    useWeddingChecklist(weddingUuid);

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
        <AlertDescription>Não foi possível carregar o checklist deste casamento.</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ListChecks className="size-5 text-primary" />
            Checklist do Planejamento
          </CardTitle>
          <CardDescription>
            Acompanhe o andamento das tarefas e marque-as como concluídas para manter seu planejamento em dia.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <WeddingChecklistTable
            tasks={tasks}
            onToggle={toggleTaskCompletion}
            isUpdating={isUpdating}
          />
        </CardContent>
      </Card>
    </div>
  );
}
