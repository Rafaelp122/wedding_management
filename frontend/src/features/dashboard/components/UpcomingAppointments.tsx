"use client";

import { Clock, Calendar, ArrowUpRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// Mock data para agora, pois eventos/agenda ainda não têm endpoint consolidado no dashboard global
const upcomingEvents = [
  { id: 1, title: 'Reunião de Alinhamento', couple: 'Sarah & Lucas', time: 'Hoje, 14:00', type: 'meeting' },
  { id: 2, title: 'Degustação de Doces', couple: 'Marina & Pedro', time: 'Amanhã, 15:30', type: 'tasting' },
  { id: 3, title: 'Visita Técnica (Local)', couple: 'Ana & Carlos', time: '15 Abr, 10:00', type: 'visit' },
  { id: 4, title: 'Pagamento: Fotógrafo', couple: 'Sarah & Lucas', time: '16 Abr', type: 'payment' },
];

export function UpcomingAppointments() {
  return (
    <Card className="flex flex-col overflow-hidden">
      <CardHeader className="bg-muted/30 border-b pb-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Clock className="size-4 text-primary" />
          Próximos Compromissos
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6 flex-1 overflow-y-auto min-h-[300px]">
        <div className="space-y-6">
          {upcomingEvents.map((event, index) => (
            <div key={event.id} className="relative pl-6">
              {/* Timeline line */}
              {index !== upcomingEvents.length - 1 && (
                <div className="absolute left-[7px] top-6 bottom-[-24px] w-px bg-border" />
              )}
              {/* Timeline dot */}
              <div className="absolute left-0 top-1.5 size-4 rounded-full border-2 border-background bg-primary shadow-sm" />

              <div className="space-y-1">
                <p className="text-sm font-semibold">{event.title}</p>
                <p className="text-xs font-medium text-primary">{event.couple}</p>
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <Calendar className="size-3" /> {event.time}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
      <div className="p-4 border-t bg-muted/30">
        <Button variant="ghost" className="w-full text-primary hover:text-primary/80 hover:bg-primary/5 h-9 text-xs gap-1">
          Ver agenda completa <ArrowUpRight className="size-3" />
        </Button>
      </div>
    </Card>
  );
}
