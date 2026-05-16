import Axios from "axios";
import { addAuthRequestInterceptor } from "./interceptors/auth-request";
import { addAuthRefreshInterceptor } from "./interceptors/auth-refresh";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function createAxiosInstance() {
  const instance = Axios.create({ baseURL });
  addAuthRequestInterceptor(instance);
  addAuthRefreshInterceptor(instance);
  return instance;
}

export const AXIOS_INSTANCE = createAxiosInstance();
