import Axios from "axios";
import { addAuthRequestInterceptor } from "./interceptors/auth-request";
import { addAuthRefreshInterceptor } from "./interceptors/auth-refresh";
import { addConnectionErrorInterceptor } from "./interceptors/connection-error";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Cria uma nova instância Axios com interceptores de autenticação
 * e tratamento de conexões pré-configurados.
 *
 * Utiliza factory (não singleton de módulo) para que cada chamada receba
 * estado de interceptor isolado — em particular, o mutex de refresh
 * (`isRefreshing`) e a fila de requisições pendentes. Isso permite testar
 * a instância em isolamento e viabiliza múltiplas instâncias simultâneas.
 */
export function createAxiosInstance() {
  const instance = Axios.create({ baseURL });
  addAuthRequestInterceptor(instance);
  addAuthRefreshInterceptor(instance);
  addConnectionErrorInterceptor(instance);
  return instance;
}

/**
 * Instância Axios compartilhada padrão. Prefira `createAxiosInstance()`
 * em testes ou quando precisar de estado de interceptor limpo.
 */
export const AXIOS_INSTANCE = createAxiosInstance();
