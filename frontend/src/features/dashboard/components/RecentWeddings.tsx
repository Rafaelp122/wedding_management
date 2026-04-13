import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "react-router-dom";
import type { WeddingOut } from "@/api/generated/v1/models";
import { formatDateBR } from "@/features/shared/utils/formatters";
import { getWeddingStatusLabel } from "@/features/weddings/utils/weddingStatus";
import { Badge } from "@/components/ui/badge";
import { ChevronRight } from "lucide-react";

interface RecentWeddingsProps {
  weddings: WeddingOut[];
  title?: string;
}

export function RecentWeddings({ weddings, title = "Próximos Casamentos" }: RecentWeddingsProps) {
  return (
    <Card className="col-span-1 lg:col-span-4 border-violet-100 dark:border-violet-900/50 shadow-sm overflow-hidden">
      <CardHeader className="border-b bg-muted/30">
        <CardTitle className="text-base font-semibold text-violet-950 dark:text-violet-50">{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="flex flex-col">
          {weddings.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-sm text-muted-foreground">
                Nenhum casamento encontrado com este filtro.
              </p>
            </div>
          ) : (
            weddings.slice(0, 5).map((wedding) => (
              <Link
                to={`/weddings/${wedding.uuid}`}
                key={wedding.uuid}
                className="group flex items-center justify-between p-4 border-b last:border-0 hover:bg-violet-50/50 dark:hover:bg-violet-900/20 transition-all duration-200"
              >
                <div className="flex flex-col gap-1">
                  <p className="text-sm font-bold text-violet-950 dark:text-violet-100 group-hover:text-primary transition-colors">
                    {wedding.groom_name} & {wedding.bride_name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatDateBR(wedding.date)} • {wedding.location}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge
                    variant={
                      wedding.status === "COMPLETED" ? "default" : "secondary"
                    }
                    className="text-[10px] uppercase tracking-wider h-5 px-2"
                  >
                    {getWeddingStatusLabel(wedding.status)}
                  </Badge>
                  <ChevronRight className="size-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                </div>
              </Link>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
