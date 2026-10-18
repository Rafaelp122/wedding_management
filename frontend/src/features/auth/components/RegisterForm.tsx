import { memo } from "react";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";

import { useAuthRegisterUser } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo, mapErrorsToForm } from "@/api/error-utils";
import { AuthRegisterUserBody } from "@/api/generated/v1/zod/auth/auth";
import type { ErrorType } from "@/api/api-client";

import { RegisterFormView } from "./RegisterFormView";

export const RegisterFormSchema = AuthRegisterUserBody.extend({
  confirm_password: z.string().min(1, "Confirme sua senha"),
}).refine((data) => data.password === data.confirm_password, {
  message: "Senhas não conferem",
  path: ["confirm_password"],
});

export type RegisterFormValues = z.input<typeof RegisterFormSchema>;
export type RegisterFormData = z.output<typeof RegisterFormSchema>;

/**
 * Smart Component para cadastro de usuários e novas contas (ADR-012, ADR-024).
 */
export const RegisterForm = memo(function RegisterForm() {
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

  const passwordValue = useWatch({ control: form.control, name: "password" });

  const onSubmit = (data: RegisterFormData) => {
    // Remove confirm_password before sending to API
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { confirm_password, ...payload } = data;
    mutate(
      { data: payload },
      {
        onSuccess: () => {
          toast.success(
            "Conta criada com sucesso! Verifique sua caixa de entrada para ativar a conta.",
          );
          navigate(
            `/verify-email-pending?email=${encodeURIComponent(data.email)}`,
          );
        },
        onError: (error: ErrorType) => {
          const hasFieldErrors = mapErrorsToForm(error, form.setError);
          if (!hasFieldErrors) {
            const { message } = getApiErrorInfo(
              error,
              "Erro ao criar conta. Verifique os dados e tente novamente.",
            );
            toast.error(message);
          }
        },
      },
    );
  };

  return (
    <RegisterFormView
      form={form}
      onSubmit={onSubmit}
      isPending={isPending}
      passwordValue={passwordValue}
    />
  );
});
