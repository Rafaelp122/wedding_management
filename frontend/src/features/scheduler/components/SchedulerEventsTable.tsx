import { Bell, Calendar, Clock } from "lucide-react";

import type { EventOut } from "@/api/generated/v1/models/eventOut";
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
  events: EventOut[];
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
                <TableHead>Lembrete</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {events.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
                    Nenhum evento cadastrado até o momento.
                  </TableCell>
                </TableRow>
              ) : (
                events.map((event) => (
                  <TableRow key={event.uuid}>
                    <TableCell className="font-medium">{event.title}</TableCell>
                    <TableCell>{weddingsByUuid.get(event.wedding) ?? event.wedding}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {EVENT_LABELS[event.event_type] ?? event.event_type}
                      </Badge>
                    </TableCell>
                    <TableCell>{formatDateTimeBR(event.start_time)}</TableCell>
                    <TableCell>
                      {event.end_time ? formatDateTimeBR(event.end_time) : "—"}
                    </TableCell>
                    <TableCell>
                      {event.reminder_enabled ? (
                        <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                          <Bell className="h-3 w-3" />
                          {event.reminder_minutes_before} min
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          Sem lembrete
                        </span>
                      )}
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
