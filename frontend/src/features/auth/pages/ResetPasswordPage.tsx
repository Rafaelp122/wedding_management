
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { z as zod } from "zod";

import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import { useAuthPasswordResetConfirm } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ErrorType } from "@/api/api-client";

import { AuthLayout } from "../components/AuthLayout";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { PasswordInput } from "../components/PasswordInput";

const ResetPasswordFormSchema = zod
  .object({
    new_password: zod.string().min(8, "A senha deve ter no mínimo 8 caracteres."),
    confirm_password: zod.string(),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "As senhas não coincidem.",
    path: ["confirm_password"],
  });

type ResetPasswordFormData = zod.infer<typeof ResetPasswordFormSchema>;

export function ResetPasswordPage() {
  useDocumentTitle("Redefinir Senha");

  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const uid = searchParams.get("uid");
  const token = searchParams.get("token");

  const { mutate, isPending } = useAuthPasswordResetConfirm<ErrorType>();

  const form = useForm<ResetPasswordFormData>({
    resolver: zodResolver(ResetPasswordFormSchema),
    defaultValues: { new_password: "", confirm_password: "" },
  });

  const isInvalidLink = !uid || !token;

  const onSubmit = (data: ResetPasswordFormData) => {
    if (isInvalidLink) return;

    mutate(
      {
        data: {
          uid,
          token,
          new_password: data.new_password,
        },
      },
      {
        onSuccess: () => {
          toast.success("Sua senha foi redefinida com sucesso! Faça login para continuar.");
          navigate("/login");
        },
        onError: (error: ErrorType) => {
          const { message } = getApiErrorInfo(error, "Erro ao redefinir senha.");
          toast.error(message);
        },
      }
    );
  };

  return (
    <AuthLayout
      heroBadgeLabel="Plataforma Sim, Aceito!"
      heroQuote='"Segurança em primeiro lugar para você e seus clientes."'
      heroBoxTitle="Atualização de Credenciais"
      heroBoxSubtitle="Defina sua nova senha"
      heroBoxBadge="Segurança"
      heroBoxLeftLabel="Criptografia"
      heroBoxLeftValue="Ativa"
      heroBoxRightLabel="Status"
      heroBoxRightValue="Protegido"
    >
      <div className="max-w-md w-full mx-auto space-y-8">
        <div className="space-y-2">
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-zinc-950 dark:text-white tracking-tight leading-tight">
            Redefinir Senha
          </h1>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            Crie uma nova senha para acessar sua conta.
          </p>
        </div>

        {isInvalidLink ? (
          <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl p-6 text-center space-y-4">
            <h3 className="text-sm font-bold text-red-800 dark:text-red-400">
              Link Inválido
            </h3>
            <p className="text-xs text-red-600 dark:text-red-500 leading-relaxed">
              O link de redefinição de senha é inválido ou expirou. Por favor, solicite um novo link.
            </p>
            <Button
              asChild
              className="w-full mt-4 bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-xl text-xs uppercase tracking-wider"
            >
              <Link to="/forgot-password">Solicitar novo link</Link>
            </Button>
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="new_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[10px] font-bold text-zinc-450 dark:text-zinc-500 uppercase tracking-wider">
                      Nova Senha
                    </FormLabel>
                    <FormControl>
                      <PasswordInput
                        placeholder="••••••••"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="confirm_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[10px] font-bold text-zinc-450 dark:text-zinc-500 uppercase tracking-wider">
                      Confirmar Nova Senha
                    </FormLabel>
                    <FormControl>
                      <PasswordInput
                        placeholder="••••••••"
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
                    Redefinindo senha...
                  </>
                ) : (
                  "Redefinir senha"
                )}
              </Button>
            </form>
          </Form>
        )}
      </div>
    </AuthLayout>
  );
}
