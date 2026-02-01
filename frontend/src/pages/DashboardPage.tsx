import { useAuthStore } from "@/stores/authStore";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function DashboardPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Bem-vindo ao seu painel de controle
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Olá, {user?.first_name}!</CardTitle>
          <CardDescription>
            Este é o início da sua nova aplicação React + Django.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Use o menu de navegação acima para acessar as diferentes áreas do
            sistema.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
