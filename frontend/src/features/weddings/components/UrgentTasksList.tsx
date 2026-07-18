import { memo } from "react";
import { Heart } from "lucide-react";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";

type UrgentTask = NonNullable<WeddingDashboardOut["urgent_tasks"]>[number];

interface UrgentTasksListProps {
  tasks: UrgentTask[];
}

export const UrgentTasksList = memo(function UrgentTasksList({ tasks }: UrgentTasksListProps) {
  if (tasks.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-muted-foreground py-8">
        <Heart className="w-8 h-8 text-muted/30 mb-3" />
        <p className="text-sm">Tudo em dia por aqui!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <div
          key={task.uuid}
          className="flex items-start gap-4 p-4 rounded-lg border border-destructive/20 bg-destructive/5"
        >
          <div className="mt-0.5">
            <div className="w-5 h-5 rounded border-2 border-destructive/30 flex items-center justify-center bg-background" />
          </div>
          <div>
            <p className="text-sm font-medium">{task.title}</p>
            <p className="text-xs text-destructive mt-1 font-medium">
              Prioridade: Alta
            </p>
          </div>
        </div>
      ))}
    </div>
  );
});
