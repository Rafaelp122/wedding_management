import type { InternalAxiosRequestConfig } from "axios";

export interface FailedQueueItem {
  resolve: (token: string) => void;
  reject: (error: Error) => void;
  config: InternalAxiosRequestConfig;
}
