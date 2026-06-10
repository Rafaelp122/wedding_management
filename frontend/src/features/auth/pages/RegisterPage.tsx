import { AuthLayout } from "../components/AuthLayout";
import { RegisterForm } from "../components/RegisterForm";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";

export default function RegisterPage() {
  useDocumentTitle("Criar Conta");

  return (
    <AuthLayout
      heroQuote="Sua arte é criar memórias inesquecíveis. Nossa ciência é garantir que os bastidores sejam impecáveis."
      heroBadgeLabel="// Fine Art Operational Excellence"
      heroBoxTitle="Template Campestre Ativo"
      heroBoxSubtitle="Marcos de faturamento e 82 tarefas configuradas"
      heroBoxBadge="100% Pronto"
      heroBoxLeftLabel="Checklists Inicial"
      heroBoxLeftValue="Fases 1 a 6 Sincronizadas"
      heroBoxRightLabel="Faturamento Padrão"
      heroBoxRightValue="Ativado Automático"
    >
      <RegisterForm />
    </AuthLayout>
  );
}
