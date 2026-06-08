import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { z } from "zod";

import { useAuthRegisterUser } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo } from "@/api/error-utils";
import { AuthRegisterUserBody } from "@/api/generated/v1/zod/auth/auth";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { PasswordInput } from "./PasswordInput";
import { SocialButtons } from "./SocialButtons";

import type { ErrorType } from "@/api/api-client";

const RegisterFormSchema = AuthRegisterUserBody.extend({
    confirm_password: z.string().min(1, "Confirme sua senha"),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Senhas não conferem",
    path: ["confirm_password"],
  });

type RegisterFormData = z.infer<typeof RegisterFormSchema>;

export function RegisterForm() {
  const navigate = useNavigate();
  const { mutate, isPending } = useAuthRegisterUser<ErrorType>();

  const form = useForm({
    resolver: zodResolver(RegisterFormSchema),
    defaultValues: {
      email: "",
      password: "",
      confirm_password: "",
      first_name: "",
      last_name: "",
      company_name: "",
    },
  });

  const onSubmit = (data: RegisterFormData) => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { confirm_password, ...payload } = data;
    mutate(
      { data: payload },
      {
        onSuccess: () => {
          toast.success("Conta criada com sucesso! Faça login para continuar.");
          navigate("/login");
        },
        onError: (error: ErrorType) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao criar conta. Verifique os dados e tente novamente.",
          );
          toast.error(message);
        },
      },
    );
  };

  return (
    <div className="max-w-md w-full mx-auto space-y-6">
      <div className="space-y-1.5">
        <h1 className="font-display font-bold text-2xl sm:text-3xl text-zinc-950 dark:text-white tracking-tight leading-tight">
          Comece o seu teste
        </h1>
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          14 dias grátis. Sem cartão de crédito. Ativação instantânea.
        </p>
      </div>

      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-3.5"
        >
          <div className="grid grid-cols-2 gap-3">
            <FormField
              control={form.control}
              name="first_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-[10px] font-bold text-zinc-450 dark:text-zinc-500 uppercase tracking-wider">
                    Nome
                  </FormLabel>
                  <FormControl>
                    <Input
                      className="text-xs border-zinc-200 dark:border-zinc-855 bg-zinc-50 dark:bg-zinc-900 rounded-xl placeholder-zinc-400 focus-visible:ring-aura-500/30 focus-visible:border-aura-500 font-medium"
                      placeholder="Helena"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="last_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-[10px] font-bold text-zinc-450 dark:text-zinc-500 uppercase tracking-wider">
                    Sobrenome
                  </FormLabel>
                  <FormControl>
                    <Input
                      className="text-xs border-zinc-200 dark:border-zinc-855 bg-zinc-50 dark:bg-zinc-900 rounded-xl placeholder-zinc-400 focus-visible:ring-aura-500/30 focus-visible:border-aura-500 font-medium"
                      placeholder="Costa"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-[10px] font-bold text-zinc-450 dark:text-zinc-500 uppercase tracking-wider">
                  E-mail de Trabalho
                </FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    className="text-xs border-zinc-200 dark:border-zinc-855 bg-zinc-50 dark:bg-zinc-900 rounded-xl placeholder-zinc-400 focus-visible:ring-aura-500/30 focus-visible:border-aura-500 font-medium"
                    placeholder="nome@agencia.com"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="company_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-[10px] font-bold text-zinc-450 dark:text-zinc-500 uppercase tracking-wider">
                  Nome da sua Assessoria / Agência
                </FormLabel>
                <FormControl>
                  <Input
                    className="text-xs border-zinc-200 dark:border-zinc-855 bg-zinc-50 dark:bg-zinc-900 rounded-xl placeholder-zinc-400 focus-visible:ring-aura-500/30 focus-visible:border-aura-500 font-medium"
                    placeholder="Sua Assessoria de Eventos"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-[10px] font-bold text-zinc-450 dark:text-zinc-500 uppercase tracking-wider">
                  Senha de Acesso
                </FormLabel>
                <FormControl>
                  <PasswordInput
                    id="regPassword"
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
                  Confirmar Senha
                </FormLabel>
                <FormControl>
                  <PasswordInput
                    id="regConfirmPassword"
                    placeholder="••••••••"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="flex items-center gap-2 pt-0.5">
            <Checkbox id="agreeTerms" />
            <label
              htmlFor="agreeTerms"
              className="text-[11px] text-zinc-500 dark:text-zinc-400 font-medium cursor-pointer"
            >
              Eu concordo com os Termos de Uso e Política de Privacidade
            </label>
          </div>

          <Button
            type="submit"
            disabled={isPending}
            className="w-full mt-2 bg-aura-600 hover:bg-aura-700 text-white font-bold py-3 rounded-xl text-xs uppercase tracking-wider shadow-lg shadow-aura-500/20 active:scale-[0.98]"
          >
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Criando sua agência...
              </>
            ) : (
              "Criar minha conta agora"
            )}
          </Button>
        </form>
      </Form>

      <div className="relative flex py-0.5 items-center">
        <div className="flex-grow border-t border-zinc-150 dark:border-zinc-800/80" />
        <span className="flex-shrink mx-4 text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
          Ou continue com
        </span>
        <div className="flex-grow border-t border-zinc-150 dark:border-zinc-800/80" />
      </div>

      <SocialButtons />

      <div className="text-center pt-1.5">
        <p className="text-xs text-zinc-550 dark:text-zinc-450">
          Já possui uma conta na plataforma?{" "}
          <Link
            to="/login"
            className="font-bold text-aura-600 dark:text-aura-400 hover:underline"
          >
            Acessar Painel ↗
          </Link>
        </p>
      </div>
    </div>
  );
}
