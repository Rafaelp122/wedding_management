/** Mapeamento de estilos Tailwind por severidade (danger, warning, success, neutral). */
export const severityStyles = {
  danger: {
    border: "border-red-200 dark:border-red-900/30",
    bg: "bg-destructive/5 dark:bg-red-950/10",
    text: "text-destructive dark:text-red-400",
    iconBg: "bg-red-50 dark:bg-red-950/20",
    iconColor: "text-destructive dark:text-red-400",
  },
  warning: {
    border: "border-amber-200 dark:border-amber-900/30",
    bg: "bg-amber-500/5 dark:bg-amber-950/10",
    text: "text-amber-600 dark:text-amber-400",
    iconBg: "bg-amber-50 dark:bg-amber-950/20",
    iconColor: "text-amber-500 dark:text-amber-400",
  },
  success: {
    border: "border-emerald-200 dark:border-emerald-900/30",
    bg: "bg-emerald-500/5 dark:bg-emerald-950/10",
    text: "text-emerald-600 dark:text-emerald-400",
    iconBg: "bg-emerald-50 dark:bg-emerald-950/20",
    iconColor: "text-emerald-500 dark:text-emerald-400",
  },
  neutral: {
    border: "border-zinc-200 dark:border-zinc-800",
    bg: "bg-aura-500/5 dark:bg-zinc-900/50",
    text: "text-zinc-900 dark:text-zinc-100",
    iconBg: "bg-aura-50 dark:bg-zinc-800/50",
    iconColor: "text-zinc-500 dark:text-zinc-400",
  },
} as const;

export type Severity = keyof typeof severityStyles;

/** Formata o nome do casal para exibição. */
export function formatWeddingName(bride: string, groom: string): string {
  return `${bride} & ${groom}`;
}

/** Pluraliza uma palavra baseada na contagem (português). */
export function pluralize(count: number, singular: string, plural?: string): string {
  return count === 1 ? singular : (plural ?? `${singular}s`);
}
