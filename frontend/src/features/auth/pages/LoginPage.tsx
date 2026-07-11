import { useCoreHealthCheck } from "@/api/generated/v1/endpoints/default/default";
import { AuthLayout } from "../components/AuthLayout";
import { LoginForm } from "../components/LoginForm";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";

export default function LoginPage() {
  useDocumentTitle("Entrar");

  // Inicia o warmup em background para mitigar cold starts
  useCoreHealthCheck();

  return (
    <AuthLayout
      heroQuote="O verdadeiro luxo reside na ausência absoluta de falhas logísticas e orçamentais nos bastidores."
      heroBadgeLabel="// Fine Art Operational Excellence"
      heroBoxTitle="Júlia & Marcos"
      heroBoxSubtitle="🗓️ 20 Set 2026 • Fazenda Vila Rica, SP"
      heroBoxBadge="58% Utilizado"
      heroBoxLeftLabel="Orçamento Máximo"
      heroBoxLeftValue="R$ 145.000,00"
      heroBoxRightLabel="Caixa Consolidado"
      heroBoxRightValue="R$ 84.500,00"
    >
      <LoginForm />
    </AuthLayout>
  );
}
