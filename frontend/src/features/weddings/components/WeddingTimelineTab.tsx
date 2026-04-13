import { AlertCircle, CalendarClock } from "lucide-react";

import { useWeddingTimeline } from "../hooks/useWeddingTimeline";
import { WeddingTimelineTable } from "./WeddingTimelineTable";

import { Alert, AlertDescription } from "@/components/ui/alert";
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
          <CardTitle className="flex items-center gap-2">
            <CalendarClock className="size-5 text-primary" />
            Cronograma de Eventos
          </CardTitle>
          <CardDescription>
            Acompanhamento detalhado de reuniões, visitas e marcos importantes do evento.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <WeddingTimelineTable events={events} />
        </CardContent>
      </Card>
    </div>
  );
}
