import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <Card className="w-full max-w-lg text-center">
        <CardHeader>
          <CardTitle className="text-3xl">Página não encontrada</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-sm text-muted-foreground">
            O caminho solicitado não existe ou ainda não foi disponibilizado.
          </p>

          <div className="flex items-center justify-center gap-3">
            <Button asChild>
              <Link to="/">Ir para o início</Link>
            </Button>
            <Button asChild variant="outline">
              <Link to="/dashboard">Ir para o painel</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
