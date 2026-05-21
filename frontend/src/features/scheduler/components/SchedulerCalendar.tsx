import { memo, useCallback, useMemo, useState } from "react";
import { Calendar, dayjsLocalizer, type SlotInfo, type View, Views } from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";
import "./SchedulerCalendar.css";
import dayjs from "dayjs";
import "dayjs/locale/pt-br";
import { Info } from "lucide-react";

import type { EventOut } from "@/api/generated/v1/models/eventOut";

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";

import { EVENT_LABELS, EVENT_COLORS } from "../constants";

const localizer = dayjsLocalizer(dayjs);

interface CalendarEvent {
  title: string;
  start: Date;
  end: Date;
  allDay: boolean;
  resource: EventOut;
}

interface EventRendererProps {
  event: CalendarEvent;
}

const EventRenderer = memo(function EventRenderer({
  event,
}: EventRendererProps) {
  const isPayment = event.resource.event_type === "pagamento";

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="truncate px-1">{event.title}</div>
      </TooltipTrigger>
      <TooltipContent>
        <div className="space-y-1 text-xs">
          <p className="font-medium">{event.resource.title}</p>
          <p>
            Tipo:{" "}
            {EVENT_LABELS[event.resource.event_type] ??
              event.resource.event_type}
          </p>
          <p>
            Início: {dayjs(event.start).format("DD/MM/YYYY HH:mm")}
          </p>
          {event.resource.end_time ? (
            <p>
              Fim:{" "}
              {dayjs(event.end).format("DD/MM/YYYY HH:mm")}
            </p>
          ) : null}
          {event.resource.location ? (
            <p>Local: {event.resource.location}</p>
          ) : null}
          {isPayment ? (
            <p className="italic text-green-600 dark:text-green-400">
              Evento gerado automaticamente (somente leitura)
            </p>
          ) : null}
        </div>
      </TooltipContent>
    </Tooltip>
  );
});

interface SchedulerCalendarProps {
  events: EventOut[];
  weddingsByUuid: Map<string, string>;
  onSelectEvent: (event: EventOut) => void;
  onSelectSlot: (startTime: Date) => void;
}

const CALENDAR_COMPONENTS = {
  event: EventRenderer,
};

export const SchedulerCalendar = memo(function SchedulerCalendar({
  events,
  weddingsByUuid,
  onSelectEvent,
  onSelectSlot,
}: SchedulerCalendarProps) {
  const [view, setView] = useState<View>(Views.MONTH);
  const [date, setDate] = useState<Date>(() => new Date());

  const calendarEvents = useMemo<CalendarEvent[]>(
    () =>
      events.map((event) => {
        const start = new Date(event.start_time);
        const end = event.end_time
          ? new Date(event.end_time)
          : new Date(start.getTime() + 60 * 60 * 1000);
        const weddingLabel =
          weddingsByUuid.get(event.wedding) ?? event.wedding.slice(0, 8);

        return {
          title: `${event.title} (${weddingLabel})`,
          start,
          end,
          allDay: false,
          resource: event,
        };
      }),
    [events, weddingsByUuid],
  );

  const eventPropGetter = useCallback(
    (event: CalendarEvent) => {
      const color = EVENT_COLORS[event.resource.event_type] ?? EVENT_COLORS.outro;
      const isPayment = event.resource.event_type === "pagamento";

      return {
        style: {
          backgroundColor: color,
          borderLeft: `3px solid ${color}`,
          borderRadius: "calc(var(--radius) - 2px)",
          opacity: isPayment ? 0.8 : 1,
          cursor: "pointer",
        },
      };
    },
    [],
  );

  const handleSelectEvent = useCallback(
    (event: CalendarEvent) => {
      onSelectEvent(event.resource);
    },
    [onSelectEvent],
  );

  const handleSelectSlot = useCallback(
    (slotInfo: SlotInfo) => {
      onSelectSlot(slotInfo.start);
    },
    [onSelectSlot],
  );

  const handleNavigate = useCallback((newDate: Date) => {
    setDate(newDate);
  }, []);

  const handleViewChange = useCallback((newView: View) => {
    setView(newView);
  }, []);

  const messages = useMemo(
    () => ({
      allDay: "Dia inteiro",
      previous: "Anterior",
      next: "Próximo",
      today: "Hoje",
      month: "Mês",
      week: "Semana",
      day: "Dia",
      agenda: "Agenda",
      date: "Data",
      time: "Hora",
      event: "Evento",
      noEventsInRange: "Nenhum evento neste período.",
      showMore: (total: number) => `+${total} mais`,
    }),
    [],
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 rounded-lg border border-info/20 bg-info/5 px-3 py-2 text-sm text-info">
        <Info className="h-4 w-4 shrink-0" />
        <span>
          Eventos de pagamento (verde) são somente leitura — gerados
          automaticamente a partir de parcelas.
        </span>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-2">
        {Object.entries(EVENT_LABELS).map(([type, label]) => (
          <Badge
            key={type}
            variant="outline"
            className="gap-1.5 border-muted-foreground/20 font-normal"
          >
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: EVENT_COLORS[type] }}
            />
            {label}
          </Badge>
        ))}
      </div>

      <TooltipProvider>
        <Calendar
          localizer={localizer}
          events={calendarEvents}
          startAccessor="start"
          endAccessor="end"
          className="min-h-[650px]"
          views={[Views.MONTH, Views.WEEK, Views.AGENDA]}
          view={view}
          date={date}
          onView={handleViewChange}
          onNavigate={handleNavigate}
          onSelectEvent={handleSelectEvent}
          onSelectSlot={handleSelectSlot}
          selectable
          eventPropGetter={eventPropGetter}
          messages={messages}
          components={CALENDAR_COMPONENTS}
        />
      </TooltipProvider>
    </div>
  );
});
