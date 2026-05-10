import { type LucideIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface MetricCardProps {
  icon: LucideIcon;
  title: string;
  value: React.ReactNode;
  subtitle?: string;
  progress?: number;
}

export function MetricCard({ icon: Icon, title, value, subtitle, progress }: MetricCardProps) {
  return (
    <Card className="flex flex-col">
      <CardHeader className="flex flex-row items-center gap-3 pb-2 space-y-0">
        <div className="p-2 bg-primary/10 text-primary rounded-lg">
          <Icon className="w-5 h-5" />
        </div>
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="mt-auto">
        <div className="flex items-end justify-between mb-2">
          <p className="text-3xl font-bold">{value}</p>
          {subtitle ? (
            <p className="text-xs text-muted-foreground mb-1">{subtitle}</p>
          ) : null}
        </div>
        {progress !== undefined ? (
          <Progress value={progress} className="h-2" />
        ) : null}
      </CardContent>
    </Card>
  );
}
