/**
 * Constantes para os modelos de cronograma de casamento.
 */

export const TEMPLATE_MAP: Record<string, string> = {
  religious_12m: "Clássico",
  beach_6m: "Campestre",
  civil_buffet_3m: "Intimista",
};

export const TEMPLATE_OPTIONS = [
  { value: "none", label: "Nenhum (Começar do zero)" },
  { value: "religious_12m", label: "Casamento Clássico em Salão" },
  { value: "beach_6m", label: "Casamento Campestre Premium" },
  { value: "civil_buffet_3m", label: "Mini Wedding Intimista" },
] as const;
