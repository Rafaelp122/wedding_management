const dateTimeFormatter = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function parseDateSafe(value: string): Date {
  if (value.includes("T") || value.includes(" ")) {
    return new Date(value);
  }
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

export function formatDateBR(
  value: string,
  options?: Intl.DateTimeFormatOptions,
): string {
  const parsed = parseDateSafe(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleDateString("pt-BR", options);
}

export function formatDateTimeBR(value: string): string {
  const parsed = parseDateSafe(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return dateTimeFormatter.format(parsed);
}

export function formatCurrencyBR(value: number): string {
  return currencyFormatter.format(value);
}

export function formatCurrencyBRCompact(
  value: number,
  maximumFractionDigits = 2,
): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 0,
    maximumFractionDigits,
  }).format(value);
}

export function parseDecimal(value?: string | null): number {
  if (!value) {
    return 0;
  }

  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : 0;
}
