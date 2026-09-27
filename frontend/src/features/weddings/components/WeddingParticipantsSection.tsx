import { memo } from "react";
import type { WeddingParticipantOut } from "@/api/generated/v1/models/weddingParticipantOut";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Users,
  UserPlus,
  Trash2,
  Mail,
  Phone,
  FileCheck,
  ShieldCheck,
} from "lucide-react";

interface WeddingParticipantsSectionProps {
  participants?: WeddingParticipantOut[];
  onAddParticipant: () => void;
  onRemoveParticipant?: (participant: WeddingParticipantOut) => void;
  isRemoving?: boolean;
}

const ROLE_LABELS: Record<string, string> = {
  BRIDE: "Noiva",
  GROOM: "Noivo",
  FINANCIAL_PAYER: "Contratante Financeiro",
  LEGAL_REPRESENTATIVE: "Representante Legal",
  OTHER: "Outro Envolvido",
};

/**
 * Componente de apresentação (Dumb) para listagem e gestão visual dos participantes do evento.
 * Segue estritamente o padrão Smart/Dumb (ADR-024).
 */
export const WeddingParticipantsSection = memo(
  function WeddingParticipantsSection({
    participants = [],
    onAddParticipant,
    onRemoveParticipant,
    isRemoving = false,
  }: WeddingParticipantsSectionProps) {
    return (
      <Card className="shadow-xs border-border/80">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/10 text-primary rounded-lg shrink-0">
              <Users className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base font-semibold text-foreground">
                Participantes & Contratantes
              </CardTitle>
              <p className="text-xs text-muted-foreground mt-0.5">
                Pessoas e partes envolvidas diretamente no evento e contratação.
              </p>
            </div>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onAddParticipant}
            className="shrink-0 gap-1.5"
          >
            <UserPlus className="h-4 w-4" />
            Vincular Participante
          </Button>
        </CardHeader>

        <CardContent className="pt-2">
          {participants.length === 0 ? (
            <div className="text-center py-6 px-4 border border-dashed rounded-lg border-muted-foreground/25">
              <Users className="h-8 w-8 mx-auto text-muted-foreground/50 mb-2" />
              <p className="text-sm font-medium text-muted-foreground">
                Nenhum participante adicional vinculado.
              </p>
              <p className="text-xs text-muted-foreground/80 mt-1">
                Adicione noivos, pais ou contratantes financeiros responsáveis pelo evento.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {participants.map((participant) => {
                const roleLabel =
                  participant.role_display ||
                  ROLE_LABELS[participant.role] ||
                  participant.role;

                return (
                  <div
                    key={participant.uuid}
                    className="flex flex-col justify-between p-3.5 rounded-lg border bg-card hover:bg-accent/30 transition-colors gap-3"
                    data-testid={`participant-card-${participant.uuid}`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-semibold text-sm text-foreground">
                            {participant.client_name}
                          </span>
                          <Badge variant="secondary" className="text-xs">
                            {roleLabel}
                          </Badge>
                          {participant.is_primary_signatory && (
                            <Badge
                              variant="default"
                              className="text-[11px] gap-1 bg-emerald-600 hover:bg-emerald-700 text-white"
                            >
                              <ShieldCheck className="h-3 w-3" />
                              Signatário
                            </Badge>
                          )}
                        </div>

                        {participant.client_cpf && (
                          <div className="text-xs text-muted-foreground flex items-center gap-1">
                            <FileCheck className="h-3 w-3 text-muted-foreground/70" />
                            <span>CPF: {participant.client_cpf}</span>
                          </div>
                        )}
                      </div>

                      {onRemoveParticipant && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-muted-foreground hover:text-destructive shrink-0"
                          onClick={() => onRemoveParticipant(participant)}
                          disabled={isRemoving}
                          aria-label={`Remover ${participant.client_name}`}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>

                    <div className="flex flex-col gap-1 text-xs text-muted-foreground border-t pt-2 border-border/50">
                      {participant.client_email && (
                        <div className="flex items-center gap-1.5 truncate">
                          <Mail className="h-3.5 w-3.5 shrink-0 text-muted-foreground/70" />
                          <span className="truncate">{participant.client_email}</span>
                        </div>
                      )}
                      {participant.client_phone && (
                        <div className="flex items-center gap-1.5">
                          <Phone className="h-3.5 w-3.5 shrink-0 text-muted-foreground/70" />
                          <span>{participant.client_phone}</span>
                        </div>
                      )}
                      {participant.notes && (
                        <p className="text-[11px] italic text-muted-foreground/80 mt-1 line-clamp-2">
                          &quot;{participant.notes}&quot;
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }
);
