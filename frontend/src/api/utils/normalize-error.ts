import Axios, { AxiosError } from "axios";

export function normalizeError(err: unknown): AxiosError | Error {
  if (Axios.isAxiosError(err)) return err;
  if (err instanceof Error) return err;
  return new Error(String(err));
}
