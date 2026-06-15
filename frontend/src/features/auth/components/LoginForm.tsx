import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

import { useAuthStore } from "@/stores/authStore";
import { useAuthObtainToken } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo, mapErrorsToForm } from "@/api/error-utils";
import type { TokenPayloadIn } from "@/api/generated/v1/models/tokenPayloadIn";
import type { TokenOut } from "@/api/generated/v1/models/tokenOut";
import { AuthObtainTokenBody } from "@/api/generated/v1/zod/auth/auth";

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
import type { AxiosResponse } from "axios";

export function LoginForm() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const { mutate, isPending } = useAuthObtainToken<ErrorType>();

  const form = useForm<TokenPayloadIn>({
    resolver: zodResolver(AuthObtainTokenBody),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = (data: TokenPayloadIn) => {
    mutate(
      { data },
      {
        onSuccess: (response: AxiosResponse<TokenOut>) => {
          const { access, refresh, user } = response.data;
          if (access && refresh && user) {
            login(access, refresh, user);
            toast.success(`Bem-vindo, ${user.first_name}!`);
            navigate("/dashboard");
          }
        },
        onError: (error: ErrorType) => {
          const hasFieldErrors = mapErrorsToForm(error, form.setError);
          if (!hasFieldErrors) {
            const { message } = getApiErrorInfo(
              error,
              "E-mail ou senha incorretos.",
            );
            toast.error(message);
          }
        },
      },
    );
  };

  return (
    <div className="max-w-md w-full mx-auto space-y-8">
      <div className="space-y-2">
        <h1 className="font-display font-bold text-2xl sm:text-3xl text-zinc-950 dark:text-white tracking-tight leading-tight">
          Acesse sua plataforma
        </h1>
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Insira suas credenciais corporativas de assessora de casamentos.
        </p>
      </div>

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

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <div className="flex justify-between items-center mb-1.5">
                  <FormLabel className="text-[10px] font-bold text-zinc-450 dark:text-zinc-500 uppercase tracking-wider">
                    Senha de Acesso
                  </FormLabel>
                  <span className="text-[10px] font-semibold text-aura-600 dark:text-aura-400 hover:underline cursor-pointer">
                    Esqueceu sua senha?
                  </span>
                </div>
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

          <div className="flex items-center gap-2 pt-1">
            <Checkbox id="rememberMe" />
            <label
              htmlFor="rememberMe"
              className="text-xs text-zinc-500 dark:text-zinc-400 font-medium cursor-pointer"
            >
              Lembrar de mim neste dispositivo
            </label>
          </div>

          <Button
            type="submit"
            disabled={isPending}
            className="w-full mt-4 bg-aura-600 hover:bg-aura-700 text-white font-bold py-3 rounded-xl text-xs uppercase tracking-wider shadow-lg shadow-aura-500/20 active:scale-[0.98]"
          >
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Validando credenciais...
              </>
            ) : (
              "Acessar painel"
            )}
          </Button>
        </form>
      </Form>

      <div className="relative flex py-1 items-center">
        <div className="flex-grow border-t border-zinc-150 dark:border-zinc-800/80" />
        <span className="flex-shrink mx-4 text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
          Ou continue com
        </span>
        <div className="flex-grow border-t border-zinc-150 dark:border-zinc-800/80" />
      </div>

      <SocialButtons />

      <div className="text-center pt-2">
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Sua agência é nova no Sim, Aceito!?{" "}
          <Link
            to="/register"
            className="font-bold text-aura-600 dark:text-aura-400 hover:underline"
          >
            Solicite seu convite ↗
          </Link>
        </p>
      </div>
    </div>
  );
}
