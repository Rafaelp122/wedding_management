import { GoogleLogin, type CredentialResponse } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { useAuthGoogleLogin } from "@/api/generated/v1/endpoints/auth/auth";
import { getApiErrorInfo } from "@/api/error-utils";
import { useAuthStore } from "@/stores/authStore";
import type { ErrorType } from "@/api/api-client";
import type { TokenOut } from "@/api/generated/v1/models/tokenOut";
import type { AxiosResponse } from "axios";

/**
 * Componente responsável pela autenticação via redes sociais (Google OAuth).
 */
export function SocialButtons() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const { mutate } = useAuthGoogleLogin<ErrorType>();

  if (!import.meta.env.VITE_GOOGLE_CLIENT_ID) {
    return null;
  }

  const handleSuccess = (credentialResponse: CredentialResponse) => {
    const credential = credentialResponse.credential;
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
  };

  const handleError = () => {
    toast.error("Falha na autenticação com o Google.");
  };

  return (
    <div className="flex justify-center w-full">
      <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
    </div>
  );
}
