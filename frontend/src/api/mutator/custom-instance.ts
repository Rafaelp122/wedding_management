import Axios, {
  AxiosError,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";
import { type DjangoErrorResponse } from "../../types/api";
import { useAuthStore } from "../../stores/authStore";

type CancellablePromise<T> = Promise<T> & { cancel?: () => void };

// A URL base sem o caminho da API, já que o Swagger lida com isso.
export const AXIOS_INSTANCE = Axios.create();

// A URL base será injetada em tempo de execução através de um interceptor
// ou de uma checagem simples. Como estamos no Vite, fazemos isso de forma segura:
const getBaseUrl = () => {
  // Ignora o erro no build process (Node/esbuild) e retorna fallback
  try {
    return import.meta.env.VITE_API_URL || "http://localhost:8000";
  } catch {
    return "http://localhost:8000";
  }
};

AXIOS_INSTANCE.defaults.baseURL = getBaseUrl();

// ----------------------------------------------------------------------
// Variáveis e Lógica da Fila de Concorrência
// ----------------------------------------------------------------------
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: AxiosError | Error) => void;
}> = [];

const processQueue = (
  error: AxiosError | Error | null,
  token: string | null = null,
) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// ----------------------------------------------------------------------
// INTERCEPTOR DE REQUEST (IDA)
// ----------------------------------------------------------------------
AXIOS_INSTANCE.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Busca o token diretamente da store do Zustand
    const token = useAuthStore.getState().accessToken;

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ----------------------------------------------------------------------
// INTERCEPTOR DE RESPONSE (VOLTA)
// ----------------------------------------------------------------------
AXIOS_INSTANCE.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Condição de gatilho: 401 Unauthorized e a requisição ainda não foi tentada
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Se já estamos no meio de um refresh, enfileira esta nova requisição
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            // Quando a fila andar, injeta o token recém-gerado
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return AXIOS_INSTANCE(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      // Inicia o processo de bloqueio
      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Busca o refresh token da store
        const refreshToken = useAuthStore.getState().refreshToken;
        if (!refreshToken) {
          throw new Error("Sem refresh token. Sessão inrecuperável.");
        }

        // Chama o backend para gerar um novo token.
        // ATENÇÃO: Usamos o Axios puro aqui para evitar loops infinitos neste interceptor
        const { data } = await Axios.post(
          `${AXIOS_INSTANCE.defaults.baseURL}/api/v1/auth/token/refresh/`,
          { refresh: refreshToken },
        );

        const newAccessToken = data.access;
        const newRefreshToken = data.refresh;

        // Atualiza a store global, não o localStorage bruto
        useAuthStore.getState().updateTokens(newAccessToken, newRefreshToken);

        // Atualiza o header da requisição original
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        // Destrava a fila e injeta o token nas requisições pendentes
        processQueue(null, newAccessToken);

        // Repete a requisição original
        return AXIOS_INSTANCE(originalRequest);
      } catch (refreshError) {
        // Lógica de tipagem estrita para acalmar o TypeScript
        const errorToProcess = Axios.isAxiosError(refreshError)
          ? refreshError
          : refreshError instanceof Error
            ? refreshError
            : new Error(String(refreshError));

        // Rejeita a fila e limpa tudo
        processQueue(errorToProcess, null);

        // DELEGA O LOGOUT PARA O ZUSTAND.
        // Isso vai mudar o isAuthenticated para false, acionando o <Navigate> do App.tsx.
        useAuthStore.getState().logout();

        return Promise.reject(errorToProcess);
      } finally {
        // Libera a trava do sistema, independente de ter falhado ou não
        isRefreshing = false;
      }
    }

    // Se o erro for outro (ex: 400, 404, 500), apenas repassa para o React Query
    return Promise.reject(error);
  },
);

// ----------------------------------------------------------------------
// MUTATOR CUSTOMIZADO PARA O ORVAL
// ----------------------------------------------------------------------
export const customInstance = <T>(
  config: AxiosRequestConfig | string,
  options?: AxiosRequestConfig,
): Promise<T> => {
  const abortController = new AbortController();

  // O Axios aceita ser chamado como Axios(url, config) ou Axios(config)
  // Mas a interface interna padrão espera um único objeto config.
  // Vamos normalizar isso:
  const finalConfig: AxiosRequestConfig =
    typeof config === "string"
      ? { url: config, ...options }
      : { ...config, ...options };

  const promise: CancellablePromise<T> = AXIOS_INSTANCE({
    ...finalConfig,
    signal: abortController.signal,
  }).then(({ data }) => data);

  promise.cancel = () => {
    abortController.abort();
  };

  return promise;
};

export default customInstance;

// Tipagem para alinhar o retorno do DRF com o Axios
export type ErrorType<T = DjangoErrorResponse> = AxiosError<T>;
