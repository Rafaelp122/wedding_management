import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface WeddingBudgetNotesCardProps {
  notes: string;
}

export function WeddingBudgetNotesCard({ notes }: WeddingBudgetNotesCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Observações Globais</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm whitespace-pre-wrap">{notes}</p>
      </CardContent>
    </Card>
  );
}
