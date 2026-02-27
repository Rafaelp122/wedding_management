import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import type { Wedding } from "@/api/generated/v1/models";
import { Badge } from "@/components/ui/badge";

export function RecentWeddings({ weddings }: { weddings: Wedding[] }) {
  return (
    <Card className="col-span-1 lg:col-span-4">
      <CardHeader>
        <CardTitle>Próximos Casamentos</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
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
                <div className="space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {wedding.groom_name} & {wedding.bride_name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(wedding.date).toLocaleDateString("pt-PT")}
                  </p>
                </div>
                <Badge
                  variant={
                    wedding.status === "COMPLETED" ? "default" : "secondary"
                  }
                >
                  {wedding.status}
                </Badge>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
