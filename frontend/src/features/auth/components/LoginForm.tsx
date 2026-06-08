import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

import { useAuthStore } from "@/stores/authStore";
import { useAuthObtainToken } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo } from "@/api/error-utils";
import type { TokenPayloadIn } from "@/api/generated/v1/models/tokenPayloadIn";
import type { TokenOut } from "@/api/generated/v1/models/tokenOut";
import { AuthObtainTokenBody } from "@/api/generated/v1/zod/auth/auth";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Checkbox } from "@/components/ui/checkbox";
import { PasswordInput } from "./PasswordInput";

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
          const { message } = getApiErrorInfo(
            error,
            "E-mail ou senha incorretos.",
          );
          toast.error(message);
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
                  <input
                    type="email"
                    className="block w-full px-3.5 py-2.5 text-xs border border-zinc-200 dark:border-zinc-850 bg-zinc-50 dark:bg-zinc-900 rounded-xl text-zinc-955 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-aura-500/30 focus:border-aura-500 transition-all font-medium"
                    placeholder="helena@aura.com"
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
                    id="loginPassword"
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

          <button
            type="submit"
            disabled={isPending}
            className="w-full mt-4 flex items-center justify-center gap-2 bg-aura-600 hover:bg-aura-700 text-white font-bold py-3 px-4 rounded-xl text-xs uppercase tracking-wider transition-all duration-250 shadow-lg shadow-aura-500/20 active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Validando credenciais...
              </>
            ) : (
              "Acessar Painel Aura"
            )}
          </button>
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
          Sua agência é nova na Aura?{" "}
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

function SocialButtons() {
  const handleGoogle = () =>
    toast.info("Integração Google SSO em desenvolvimento.");

  const handleApple = () =>
    toast.info("Integração Apple ID em desenvolvimento.");

  return (
    <div className="grid grid-cols-2 gap-3">
      <button
        type="button"
        onClick={handleGoogle}
        className="flex items-center justify-center gap-2 py-2.5 px-4 border border-zinc-200 dark:border-zinc-800 rounded-xl text-xs font-semibold hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors bg-transparent"
      >
        <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
          <path
            fill="#EA4335"
            d="M12.24 10.285V14.4h6.887c-.275 1.565-1.88 4.604-6.887 4.604-4.33 0-7.859-3.578-7.859-8s3.53-8 7.86-8c2.46 0 4.105 1.025 5.047 1.926l3.245-3.125C18.265 1.77 15.483 1 12.24 1 5.92 1 12.24s4.92 11.24 11.24 11.24c6.6 0 11-4.64 11-11.24 0-.75-.08-1.33-.235-1.955H12.24z"
          />
        </svg>
        Google
      </button>
      <button
        type="button"
        onClick={handleApple}
        className="flex items-center justify-center gap-2 py-2.5 px-4 border border-zinc-200 dark:border-zinc-800 rounded-xl text-xs font-semibold hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors bg-transparent"
      >
        <svg className="w-4 h-4 shrink-0 fill-current" viewBox="0 0 24 24">
          <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 4.17c.66-.81 1.11-1.93.99-3.06-1 .04-2.15.65-2.87 1.49-.62.71-1.16 1.85-1.01 2.96 1.1.09 2.19-.55 2.89-1.39z" />
        </svg>
        Apple ID
      </button>
    </div>
  );
}
