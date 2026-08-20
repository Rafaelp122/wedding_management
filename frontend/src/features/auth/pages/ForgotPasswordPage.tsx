import { useState } from "react";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import { useAuthPasswordResetRequest } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo } from "@/api/error-utils";
import type { PasswordResetRequestIn } from "@/api/generated/v1/models/passwordResetRequestIn";
import type { ErrorType } from "@/api/api-client";
import { AuthPasswordResetRequestBody } from "@/api/generated/v1/zod/auth/auth";

import { AuthLayout } from "../components/AuthLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

export function ForgotPasswordPage() {
  useDocumentTitle("Recuperar Senha");

  const [isSuccess, setIsSuccess] = useState(false);
  const { mutate, isPending } = useAuthPasswordResetRequest<ErrorType>();

  const form = useForm<PasswordResetRequestIn>({
    resolver: zodResolver(AuthPasswordResetRequestBody),
    defaultValues: { email: "" },
  });

  const onSubmit = (data: PasswordResetRequestIn) => {
    mutate(
      { data },
      {
        onSuccess: () => {
          setIsSuccess(true);
        },
        onError: (error: ErrorType) => {
          const { message } = getApiErrorInfo(
            error,
            "Ocorreu um erro ao processar sua solicitação."
          );
          toast.error(message);
        },
      }
    );
  };

  return (
    <AuthLayout
      heroBadgeLabel="Plataforma Sim, Aceito!"
      heroQuote='"A tranquilidade de ter todos os detalhes sob controle."'
      heroBoxTitle="Recuperação Segura"
      heroBoxSubtitle="Acesso protegido à sua conta"
      heroBoxBadge="Segurança"
      heroBoxLeftLabel="Mecanismo"
      heroBoxLeftValue="Token Temporário"
      heroBoxRightLabel="Status"
      heroBoxRightValue="Ativo"
    >
      <div className="max-w-md w-full mx-auto space-y-8">
        <div className="space-y-2">
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-zinc-950 dark:text-white tracking-tight leading-tight">
            Recuperar Senha
          </h1>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            Esqueceu sua senha? Não se preocupe. Digite seu e-mail abaixo.
          </p>
        </div>

        {isSuccess ? (
          <div className="bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl p-6 text-center space-y-4">
            <h3 className="text-sm font-bold text-emerald-800 dark:text-emerald-400">
              E-mail enviado!
            </h3>
            <p className="text-xs text-emerald-600 dark:text-emerald-500 leading-relaxed">
              Se o e-mail estiver cadastrado em nossa plataforma, você receberá um link para redefinir sua senha em instantes.
            </p>
            <Button
              asChild
              className="w-full mt-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 rounded-xl text-xs uppercase tracking-wider"
            >
              <Link to="/login">Voltar ao Login</Link>
            </Button>
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[10px] font-bold text-zinc-450 dark:text-zinc-500 uppercase tracking-wider">
                      Endereço de E-mail
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        className="text-xs border-zinc-200 dark:border-zinc-850 bg-zinc-50 dark:bg-zinc-900 rounded-xl placeholder-zinc-400 focus-visible:ring-aura-500/30 focus-visible:border-aura-500 font-medium"
                        placeholder="helena@simaceito.com"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button
                type="submit"
                disabled={isPending}
                className="w-full mt-4 bg-aura-600 hover:bg-aura-700 text-white font-bold py-3 rounded-xl text-xs uppercase tracking-wider shadow-lg shadow-aura-500/20 active:scale-[0.98]"
              >
                {isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Enviando solicitação...
                  </>
                ) : (
                  "Enviar link de recuperação"
                )}
              </Button>
            </form>
          </Form>
        )}

        {!isSuccess && (
          <div className="text-center pt-2">
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Lembrou sua senha?{" "}
              <Link
                to="/login"
                className="font-bold text-aura-600 dark:text-aura-400 hover:underline"
              >
                Voltar ao Login ↗
              </Link>
            </p>
          </div>
        )}
      </div>
    </AuthLayout>
  );
}
