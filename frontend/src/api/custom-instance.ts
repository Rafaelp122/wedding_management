import type { AxiosRequestConfig, AxiosResponse, AxiosError } from "axios";
import type { DjangoErrorResponse } from "./types/backend";
import { AXIOS_INSTANCE } from "./axios-instance";

export const customInstance = async <T>(
  config: AxiosRequestConfig | string,
  options?: AxiosRequestConfig,
): Promise<AxiosResponse<T>> => {
  const finalConfig: AxiosRequestConfig =
    typeof config === "string"
      ? { url: config, ...options }
      : { ...config, ...options };

  return AXIOS_INSTANCE.request<T>(finalConfig);
};

export type ErrorType<T = DjangoErrorResponse> = AxiosError<T>;
