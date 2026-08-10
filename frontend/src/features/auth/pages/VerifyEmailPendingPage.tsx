import { useSearchParams, Link } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, Mail, ArrowLeft } from "lucide-react";
import { useAuthResendVerification } from "@/api/generated/v1/endpoints/auth/auth";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import { AuthLayout } from "../components/AuthLayout";
import { Button } from "@/components/ui/button";
import type { ErrorType } from "@/api/api-client";
import { getApiErrorInfo } from "@/api/error-utils";

export function VerifyEmailPendingPage() {
  useDocumentTitle("Ativação de Conta Pendente");
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email") || "";

  const { mutate, isPending } = useAuthResendVerification<ErrorType>();

  const handleResend = () => {
    if (!email) return;
    mutate(
      { data: { email } },
      {
        onSuccess: () => {
          toast.success("Novo e-mail de confirmação enviado com sucesso!");
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao reenviar e-mail.");
          toast.error(message);
        }
      }
    );
  };

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
      <div className="max-w-md w-full mx-auto flex flex-col items-center justify-center space-y-6 text-center">
        <div className="bg-aura-100 dark:bg-aura-900/30 p-4 rounded-full">
          <Mail className="w-10 h-10 text-aura-600 dark:text-aura-400" />
        </div>

        <div className="space-y-2">
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-zinc-950 dark:text-white tracking-tight leading-tight">
            Verifique seu e-mail
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Enviamos um e-mail de confirmação para <span className="font-semibold text-zinc-900 dark:text-zinc-100">{email || "seu endereço de e-mail"}</span>. Clique no link enviado para ativar sua conta.
          </p>
        </div>

        <div className="w-full space-y-4 pt-4">
          <Button
            onClick={handleResend}
            disabled={!email || isPending}
            variant="outline"
            className="w-full border-zinc-200 dark:border-zinc-800"
          >
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Reenviando...
              </>
            ) : (
              "Reenviar e-mail de ativação"
            )}
          </Button>

          <Button variant="ghost" className="w-full" asChild>
            <Link to="/login">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar para o login
            </Link>
          </Button>
        </div>
      </div>
    </AuthLayout>
  );
}
