import { useCallback, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { AlertCircle, CalendarClock, Plus } from "lucide-react";

import { useWeddingTimeline } from "../../hooks/useTimeline";
import { WeddingTimelineTable } from "./TimelineTable";
import { CreateEventDialog } from "./CreateEventDialog";
import { getSchedulerEventsListQueryKey } from "@/api/generated/v1/endpoints/scheduler/scheduler";

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

interface WeddingTimelineTabProps {
  weddingUuid: string;
}

export function WeddingTimelineTab({ weddingUuid }: WeddingTimelineTabProps) {
  const { events, isLoading, error } = useWeddingTimeline(weddingUuid);
  const queryClient = useQueryClient();

  const [dialogOpen, setDialogOpen] = useState(false);

  const handleSuccess = useCallback(() => {
    setDialogOpen(false);
    queryClient.invalidateQueries({ queryKey: getSchedulerEventsListQueryKey() });
  }, [queryClient]);

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
          Não foi possível carregar o cronograma deste casamento.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CalendarClock className="size-5 text-primary" />
              <CardTitle>Cronograma de Eventos</CardTitle>
            </div>
            <Button
              size="sm"
              className="gap-1.5"
              onClick={() => setDialogOpen(true)}
            >
              <Plus className="h-4 w-4" />
              Novo Evento
            </Button>
          </div>
          <CardDescription>
            Acompanhamento detalhado de reuniões, visitas e marcos importantes do evento.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <WeddingTimelineTable events={events} />
        </CardContent>
      </Card>

      <CreateEventDialog
        weddingUuid={weddingUuid}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onSuccess={handleSuccess}
      />
    </div>
  );
}
