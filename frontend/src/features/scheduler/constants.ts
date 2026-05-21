export const EVENT_TYPE_OPTIONS = [
  { value: "reuniao", label: "Reunião" },
  { value: "visita", label: "Visita Técnica" },
  { value: "degustacao", label: "Degustação" },
  { value: "outro", label: "Outro" },
] as const;

export const RECURRENCE_OPTIONS = [
  { value: "none", label: "Nenhuma" },
  { value: "semanal", label: "Semanal" },
  { value: "quinzenal", label: "Quinzenal" },
  { value: "mensal", label: "Mensal" },
] as const;

export const EVENT_LABELS: Record<string, string> = {
  reuniao: "Reunião",
  pagamento: "Pagamento",
  visita: "Visita Técnica",
  degustacao: "Degustação",
  outro: "Outro",
};

export const EVENT_COLORS: Record<string, string> = {
  reuniao: "#3B82F6",
  pagamento: "#22C55E",
  visita: "#A855F7",
  degustacao: "#F97316",
  outro: "#6B7280",
};
