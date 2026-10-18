import { memo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { useAuthStore } from "@/stores/authStore";
import { useAuthObtainToken } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo, mapErrorsToForm } from "@/api/error-utils";
import type { TokenPayloadIn } from "@/api/generated/v1/models/tokenPayloadIn";
import type { TokenOut } from "@/api/generated/v1/models/tokenOut";
import { AuthObtainTokenBody } from "@/api/generated/v1/zod/auth/auth";
import type { ErrorType } from "@/api/api-client";
import type { AxiosResponse } from "axios";

import { LoginFormView } from "./LoginFormView";

/**
 * Smart Component para autenticação de usuários (ADR-012, ADR-024).
 */
export const LoginForm = memo(function LoginForm() {
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
            const { message, code } = getApiErrorInfo(
              error,
              "E-mail ou senha incorretos.",
            );
            if (code === "email_not_verified") {
              toast.error("Sua conta ainda não foi ativada.", {
                action: {
                  label: "Ativar conta",
                  onClick: () =>
                    navigate(
                      `/verify-email-pending?email=${encodeURIComponent(data.email)}`,
                    ),
                },
              });
            } else if (code === "account_locked") {
              toast.error(message, {
                duration: 8000,
                description:
                  "Por motivos de segurança, aguarde o tempo indicado antes de tentar novamente.",
              });
            } else {
              toast.error(message);
            }
          }
        },
      },
    );
  };

  return (
    <LoginFormView
      form={form}
      onSubmit={onSubmit}
      isPending={isPending}
    />
  );
});
