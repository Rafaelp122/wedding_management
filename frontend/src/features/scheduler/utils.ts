import { formatISO, parseISO } from "date-fns";

/**
 * Converte string datetime-local (YYYY-MM-DDTHH:MM) para ISO 8601 com timezone.
 */
export function toISODateTime(localValue: string): string {
  if (!localValue) return "";
  // Adiciona timezone local ao valor antes de converter
  return formatISO(parseISO(localValue));
}

/**
 * Converte string ISO 8601 para datetime-local (YYYY-MM-DDTHH:MM) para
 * exibição em <input type="datetime-local">.
 */
export function toDateTimeLocalValue(isoString: string): string {
  if (!isoString) return "";
  const d = new Date(isoString);
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}
