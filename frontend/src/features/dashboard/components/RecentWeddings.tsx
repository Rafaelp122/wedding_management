import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import type { WeddingOut } from "@/api/generated/v1/models";
import { formatDateBR } from "@/features/shared/utils/formatters";
import { getWeddingStatusLabel } from "@/features/weddings/utils/weddingStatus";
import { Badge } from "@/components/ui/badge";

export function RecentWeddings({ weddings }: { weddings: WeddingOut[] }) {
  return (
    <Card className="col-span-1 lg:col-span-4">
      <CardHeader>
        <CardTitle>Próximos Casamentos</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-6">
          {weddings.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Nenhum casamento agendado.
            </p>
          ) : (
            weddings.slice(0, 5).map((wedding) => (
              <div
                key={wedding.uuid}
                className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
              >
                <div className="flex flex-col gap-1">
                  <p className="text-sm font-medium leading-none">
                    {wedding.groom_name} & {wedding.bride_name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatDateBR(wedding.date)}
                  </p>
                </div>
                <Badge
                  variant={
                    wedding.status === "COMPLETED" ? "default" : "secondary"
                  }
                >
                  {getWeddingStatusLabel(wedding.status)}
                </Badge>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
