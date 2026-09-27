import { useState } from "react";
import { AlertCircle, ListChecks, Plus } from "lucide-react";

import { useWeddingChecklist } from "../../hooks/useChecklist";
import { WeddingChecklistTable } from "./ChecklistTable";
import { CompressedTimelineAlert } from "../CompressedTimelineAlert";
import { CreateTaskDialog } from "./CreateTaskDialog";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface WeddingChecklistTabProps {
  weddingUuid: string;
}

export function WeddingChecklistTab({ weddingUuid }: WeddingChecklistTabProps) {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
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

  const completedCount = tasks.filter((t) => t.is_completed).length;
  const totalCount = tasks.length;
  const progressPercentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="flex flex-col gap-6">
      <CompressedTimelineAlert weddingUuid={weddingUuid} />

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <ListChecks className="size-5 text-primary" />
                  Checklist Operacional
                </CardTitle>
                <CardDescription>
                  Acompanhe o andamento das tarefas e marque-as como concluídas para manter seu planejamento em dia.
                </CardDescription>
              </div>
              <div className="flex items-center gap-4 shrink-0">
                {totalCount > 0 && (
                  <div className="text-right">
                    <span className="text-sm font-semibold text-foreground">
                      {progressPercentage}%
                    </span>
                    <p className="text-xs text-muted-foreground">
                      {completedCount} de {totalCount} concluídas
                    </p>
                  </div>
                )}
                <Button
                  size="sm"
                  onClick={() => setIsCreateOpen(true)}
                  className="gap-1.5 cursor-pointer"
                >
                  <Plus className="size-4" />
                  Novo Item
                </Button>
              </div>
            </div>

            {totalCount > 0 && (
              <div className="w-full">
                <Progress
                  value={progressPercentage}
                  className="h-2"
                  aria-label={`Progresso Operacional: ${completedCount} de ${totalCount} tarefas concluídas`}
                />
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <WeddingChecklistTable
            tasks={tasks}
            onToggle={toggleTaskCompletion}
            isUpdating={isUpdating}
            onCreateClick={() => setIsCreateOpen(true)}
          />
        </CardContent>
      </Card>

      <CreateTaskDialog
        weddingUuid={weddingUuid}
        open={isCreateOpen}
        onOpenChange={setIsCreateOpen}
      />
    </div>
  );
}
