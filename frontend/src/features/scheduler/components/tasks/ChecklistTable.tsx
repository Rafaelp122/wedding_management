import type { TaskOut } from "@/api/generated/v1/models/taskOut";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";

interface WeddingChecklistTableProps {
  tasks: TaskOut[];
  onToggle: (uuid: string, currentStatus: boolean) => void;
  isUpdating: boolean;
}

export function WeddingChecklistTable({
  tasks,
  onToggle,
  isUpdating,
}: WeddingChecklistTableProps) {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground border rounded-md">
        <p className="text-sm">Nenhuma tarefa registrada para o planejamento deste casamento.</p>
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
          <div className="flex flex-col gap-1 leading-none">
            <label
              htmlFor={`task-${task.uuid}`}
              className={cn(
                "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer",
                task.is_completed && "line-through text-muted-foreground"
              )}
            >
              {task.title}
            </label>
            {task.description && (
              <p className={cn("text-sm text-muted-foreground", task.is_completed && "line-through opacity-70")}>
                {task.description}
              </p>
            )}
            {task.due_date && (
              <p className="text-xs text-muted-foreground pt-1">
                Prazo: {new Date(task.due_date).toLocaleDateString("pt-BR")}
              </p>
            )}
          </div>
        </Card>
      ))}
    </div>
  );
}
