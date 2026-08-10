import { useEffect, useRef, useState } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { Loader2, CheckCircle2, XCircle, ArrowLeft, ArrowRight } from "lucide-react";
import { useAuthVerifyEmail } from "@/api/generated/v1/endpoints/auth/auth";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import { AuthLayout } from "../components/AuthLayout";
import { Button } from "@/components/ui/button";
import type { ErrorType } from "@/api/api-client";

export function VerifyEmailPage() {
  useDocumentTitle("Ativação de Conta");
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const uid = searchParams.get("uid");
  const token = searchParams.get("token");

  const hasAttempted = useRef(false);
  const [status, setStatus] = useState<"loading" | "success" | "error" | "invalid">("loading");

  const { mutate } = useAuthVerifyEmail<ErrorType>();

  useEffect(() => {
    if (!uid || !token) {
      setStatus("invalid");
      return;
    }

    if (!hasAttempted.current) {
      hasAttempted.current = true;
      mutate(
        { data: { uid, token } },
        {
          onSuccess: () => {
            setStatus("success");
          },
          onError: () => {
            setStatus("error");
          }
        }
      );
    }
  }, [uid, token, mutate]);

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
        {status === "loading" && (
          <>
            <div className="bg-aura-100 dark:bg-aura-900/30 p-4 rounded-full">
              <Loader2 className="w-10 h-10 text-aura-600 dark:text-aura-400 animate-spin" />
            </div>
            <div className="space-y-2">
              <h1 className="font-display font-bold text-2xl sm:text-3xl text-zinc-950 dark:text-white tracking-tight leading-tight">
                Ativando sua conta...
              </h1>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Aguarde enquanto verificamos suas credenciais.
              </p>
            </div>
          </>
        )}

        {status === "success" && (
          <>
            <div className="bg-emerald-100 dark:bg-emerald-900/30 p-4 rounded-full">
              <CheckCircle2 className="w-10 h-10 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div className="space-y-2">
              <h1 className="font-display font-bold text-2xl sm:text-3xl text-zinc-950 dark:text-white tracking-tight leading-tight">
                Conta Ativada!
              </h1>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Sua conta foi ativada com sucesso! Você já pode acessar a plataforma.
              </p>
            </div>
            <div className="w-full pt-4">
              <Button className="w-full bg-aura-600 hover:bg-aura-700" asChild>
                <Link to="/login">
                  Acessar painel
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </Button>
            </div>
          </>
        )}

        {(status === "error" || status === "invalid") && (
          <>
            <div className="bg-red-100 dark:bg-red-900/30 p-4 rounded-full">
              <XCircle className="w-10 h-10 text-red-600 dark:text-red-400" />
            </div>
            <div className="space-y-2">
              <h1 className="font-display font-bold text-2xl sm:text-3xl text-zinc-950 dark:text-white tracking-tight leading-tight">
                Erro na Ativação
              </h1>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Link de verificação inválido ou expirado.
              </p>
            </div>
            <div className="w-full space-y-4 pt-4">
              <Button
                variant="outline"
                className="w-full border-zinc-200 dark:border-zinc-800"
                onClick={() => navigate("/verify-email-pending")}
              >
                Reenviar e-mail de ativação
              </Button>
              <Button variant="ghost" className="w-full" asChild>
                <Link to="/login">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Voltar para o login
                </Link>
              </Button>
            </div>
          </>
        )}
      </div>
    </AuthLayout>
  );
}
