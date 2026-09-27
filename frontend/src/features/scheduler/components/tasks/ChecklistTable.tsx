import { memo } from "react";
import type { TaskOut } from "@/api/generated/v1/models/taskOut";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { formatDateBR } from "@/lib/formatters";
import { cn } from "@/lib/utils";

import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

interface WeddingChecklistTableProps {
  tasks: TaskOut[];
  onToggle: (uuid: string, currentStatus: boolean) => void;
  isUpdating: boolean;
  onCreateClick?: () => void;
}

const PRIORITY_LABELS: Record<string, string> = {
  LOW: "Baixa",
  MEDIUM: "Média",
  HIGH: "Alta",
  URGENT: "Urgente",
};

const PRIORITY_BADGE_CLASSES: Record<string, string> = {
  LOW: "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300",
  MEDIUM: "bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950 dark:text-blue-200",
  HIGH: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950 dark:text-amber-200",
  URGENT: "bg-red-100 text-red-800 border-red-200 dark:bg-red-950 dark:text-red-200",
};

export const WeddingChecklistTable = memo(function WeddingChecklistTable({
  tasks,
  onToggle,
  isUpdating,
  onCreateClick,
}: WeddingChecklistTableProps) {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground border border-dashed rounded-md flex flex-col items-center justify-center gap-3">
        <p className="text-sm">Nenhuma tarefa registrada para o planejamento deste casamento.</p>
        {onCreateClick && (
          <Button
            variant="outline"
            size="sm"
            onClick={onCreateClick}
            className="gap-1.5 cursor-pointer"
          >
            <Plus className="size-4" />
            Adicionar Tarefa
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {tasks.map((task) => (
        <Card
          key={task.uuid}
          className={cn(
            "flex flex-row items-start gap-3 p-4 transition-colors",
            task.is_completed && "bg-muted/50"
          )}
        >
          <Checkbox
            id={`task-${task.uuid}`}
            checked={task.is_completed}
            disabled={isUpdating}
            onCheckedChange={() => onToggle(task.uuid, task.is_completed)}
            className="mt-1"
          />
          <div className="flex flex-col gap-1 leading-none w-full">
            <div className="flex flex-wrap items-center gap-2">
              <label
                htmlFor={`task-${task.uuid}`}
                className={cn(
                  "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer",
                  task.is_completed && "line-through text-muted-foreground"
                )}
              >
                {task.title}
              </label>

              {task.priority && PRIORITY_LABELS[task.priority] && (
                <Badge
                  variant="outline"
                  className={cn(
                    "text-xs font-normal",
                    PRIORITY_BADGE_CLASSES[task.priority]
                  )}
                >
                  {PRIORITY_LABELS[task.priority]}
                </Badge>
              )}

              {task.is_overdue && !task.is_completed && (
                <Badge variant="destructive" className="text-xs font-normal">
                  Atrasada ({task.days_overdue} {task.days_overdue === 1 ? "dia" : "dias"})
                </Badge>
              )}
            </div>

            {task.description && (
              <p className={cn("text-sm text-muted-foreground mt-1", task.is_completed && "line-through opacity-70")}>
                {task.description}
              </p>
            )}

            <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground pt-1">
              {task.due_date && (
                <span>Prazo: {formatDateBR(task.due_date)}</span>
              )}
              {task.is_completed && task.completed_at && (
                <span>Concluída em: {formatDateBR(task.completed_at)}</span>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
});
