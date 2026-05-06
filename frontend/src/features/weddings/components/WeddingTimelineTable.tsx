import type { EventOut } from "@/api/generated/v1/models/eventOut";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface WeddingTimelineTableProps {
  events: EventOut[];
}

export function WeddingTimelineTable({ events }: WeddingTimelineTableProps) {
  if (events.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground border rounded-md">
        <p className="text-sm">Nenhum evento registrado no cronograma para este evento.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Evento</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Data/Hora Início</TableHead>
            <TableHead>Local</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {events.map((event) => (
            <TableRow key={event.uuid}>
              <TableCell className="font-medium">{event.title}</TableCell>
              <TableCell>
                <Badge variant="outline" className="capitalize">
                  {event.event_type}
                </Badge>
              </TableCell>
              <TableCell>
                {new Date(event.start_time).toLocaleString("pt-BR", {
                  dateStyle: "short",
                  timeStyle: "short",
                })}
              </TableCell>
              <TableCell className="max-w-[200px] truncate" title={event.location || ""}>
                {event.location || "N/A"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
