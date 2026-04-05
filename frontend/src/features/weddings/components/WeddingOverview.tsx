import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import type { WeddingOut } from "@/api/generated/v1/models";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Calendar, MapPin, Users, Clock } from "lucide-react";

interface WeddingOverviewProps {
  wedding: WeddingOut;
}

const STATUS_CONFIG = {
  IN_PROGRESS: { label: "Em Andamento", variant: "default" as const },
  COMPLETED: { label: "Concluído", variant: "secondary" as const },
  CANCELED: { label: "Cancelado", variant: "destructive" as const },
};

export function WeddingOverview({ wedding }: WeddingOverviewProps) {
  const statusConfig = STATUS_CONFIG[wedding.status as keyof typeof STATUS_CONFIG] ||
    STATUS_CONFIG.IN_PROGRESS;

  const formattedDate = format(new Date(wedding.date), "dd 'de' MMMM 'de' yyyy", {
    locale: ptBR,
  });

  const createdAt = format(new Date(wedding.created_at), "dd/MM/yyyy 'às' HH:mm", {
    locale: ptBR,
  });

  return (
    <div className="space-y-6">
      {/* Header com nomes dos noivos */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h2 className="text-3xl font-bold">
            {wedding.groom_name} & {wedding.bride_name}
          </h2>
          <Badge variant={statusConfig.variant}>{statusConfig.label}</Badge>
        </div>
        <p className="text-muted-foreground">
          Casamento criado em {createdAt}
        </p>
      </div>

      {/* Grid de informações principais */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data do Evento</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formattedDate}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Local</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{wedding.location}</div>
          </CardContent>
        </Card>

        {wedding.expected_guests && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Convidados Esperados
              </CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{wedding.expected_guests}</div>
              <p className="text-xs text-muted-foreground">pessoas</p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Tempo até o Evento
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(() => {
                const today = new Date();
                const eventDate = new Date(wedding.date);
                const diffTime = eventDate.getTime() - today.getTime();
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

                if (diffDays < 0) {
                  return "Evento realizado";
                } else if (diffDays === 0) {
                  return "Hoje!";
                } else if (diffDays === 1) {
                  return "Amanhã";
                } else {
                  return `${diffDays} dias`;
                }
              })()}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Informações adicionais */}
      <Card>
        <CardHeader>
          <CardTitle>Informações Adicionais</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="text-muted-foreground">UUID</div>
            <div className="font-mono text-xs">{wedding.uuid}</div>

            <div className="text-muted-foreground">Última Atualização</div>
            <div>
              {format(new Date(wedding.updated_at), "dd/MM/yyyy 'às' HH:mm", {
                locale: ptBR,
              })}
            </div>

            <div className="text-muted-foreground">Status</div>
            <div>{statusConfig.label}</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
