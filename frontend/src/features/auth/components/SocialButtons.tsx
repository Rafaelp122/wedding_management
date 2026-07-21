import { useGoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

import { useAuthGoogleLogin } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo } from "@/api/error-utils";
import { useAuthStore } from "@/stores/authStore";
import { Button } from "@/components/ui/button";
import type { ErrorType } from "@/api/api-client";
import type { TokenOut } from "@/api/generated/v1/models/tokenOut";
import type { AxiosResponse } from "axios";

/**
 * Componente responsável pela autenticação via redes sociais (Google OAuth).
 */
export function SocialButtons() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const { mutate, isPending } = useAuthGoogleLogin<ErrorType>();

  const handleGoogleLogin = useGoogleLogin({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onSuccess: (response: any) => {
      const credential = response?.credential;
      if (credential) {
        mutate(
          { data: { id_token: credential } },
          {
            onSuccess: (res: AxiosResponse<TokenOut>) => {
              const { access, refresh, user } = res.data;
              if (access && refresh && user) {
                login(access, refresh, user);
                toast.success(`Bem-vindo, ${user.first_name}!`);
                navigate("/dashboard");
              }
            },
            onError: (error: ErrorType) => {
              const { message } = getApiErrorInfo(
                error,
                "Falha na autenticação com o Google.",
              );
              toast.error(message);
            },
          },
        );
      }
    },
    onError: () => {
      toast.error("Falha na autenticação com o Google.");
    },
  });

  return (
    <div className="flex justify-center">
      <Button
        type="button"
        variant="outline"
        disabled={isPending}
        className="w-full border-zinc-200 dark:border-zinc-800 rounded-xl text-sm font-semibold hover:bg-zinc-50 dark:hover:bg-zinc-900 bg-transparent h-11"
        onClick={() => handleGoogleLogin()}
      >
        {isPending ? (
          <Loader2 className="w-4 h-4 animate-spin mr-2" />
        ) : (
          <svg className="w-4 h-4 shrink-0 mr-2" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
          </svg>
        )}
        Google
      </Button>
    </div>
  );
}
