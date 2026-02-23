import { useAuthStore } from "../stores/authStore";

// Definindo a interface para o cast seguro
interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
}

export const customInstance = async <T>(
  url: string,
  config: RequestInit & { params?: Record<string, unknown> },
): Promise<T> => {
  const { params, ...rest } = config;

  // 1. Configuração da Base URL (Driblando o aviso do Orval com cast seguro)
  const baseURL =
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (import.meta as any)["env"]["VITE_API_URL"] ||
    "http://localhost:8000/api/v1";

  // 2. Construção da URL com Query Params
  const fullUrl = new URL(`${baseURL}${url}`);
  if (params) {
    Object.keys(params).forEach((key) => {
      const value = params[key];
      if (value !== undefined && value !== null) {
        fullUrl.searchParams.append(key, String(value));
      }
    });
  }

  // 3. Injeção do Token de Autenticação
  const token = useAuthStore.getState().token;
  const headers = new Headers(rest.headers);
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  // 4. Execução do Fetch
  const response = await fetch(fullUrl.toString(), {
    ...rest,
    headers,
  });

  // 5. Tratamento de Erro
  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro desconhecido" }));

    throw {
      message: errorData.detail || errorData.message || "Erro na requisição",
      status: response.status,
      data: errorData,
    };
  }

  return response.json();
};

export default customInstance;
