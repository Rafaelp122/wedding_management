import { Calendar } from "lucide-react";

import type { AppointmentOut } from "@/api/generated/v1/models";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDateTimeBR } from "@/features/shared/utils/formatters";

const EVENT_LABELS: Record<string, string> = {
  reuniao: "Reunião",
  pagamento: "Pagamento",
  visita: "Visita Técnica",
  degustacao: "Degustação",
  outro: "Outro",
};

interface SchedulerEventsTableProps {
  events: AppointmentOut[];
  weddingsByUuid: Map<string, string>;
}

export function SchedulerEventsTable({
  events,
  weddingsByUuid,
}: SchedulerEventsTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          Próximos compromissos
        </CardTitle>
        <CardDescription>
          Eventos ordenados por data para facilitar o acompanhamento operacional.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Título</TableHead>
                <TableHead>Casamento</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Início</TableHead>
                <TableHead>Fim</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {events.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground">
                    Nenhum evento cadastrado até o momento.
                  </TableCell>
                </TableRow>
              ) : (
                events.map((event) => (
                  <TableRow key={event.uuid}>
                    <TableCell className="font-medium">{event.title}</TableCell>
                    <TableCell>{weddingsByUuid.get(event.event_uuid!) ?? event.event_uuid}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {EVENT_LABELS[event.event_type] ?? event.event_type}
                      </Badge>
                    </TableCell>
                    <TableCell>{formatDateTimeBR(event.start_time)}</TableCell>
                    <TableCell>
                      {event.end_time ? formatDateTimeBR(event.end_time) : "—"}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
