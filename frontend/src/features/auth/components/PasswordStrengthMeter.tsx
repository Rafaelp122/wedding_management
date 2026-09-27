import { calculatePasswordStrength } from "../utils/password-strength";

interface PasswordStrengthMeterProps {
  password?: string;
  className?: string;
}

export function PasswordStrengthMeter({
  password = "",
  className = "",
}: PasswordStrengthMeterProps) {
  if (!password) {
    return null;
  }

  const { score, label, colorClass, feedback } = calculatePasswordStrength(password);

  return (
    <div className={`space-y-1.5 pt-1 ${className}`} aria-live="polite">
      <div className="flex items-center justify-between text-[10px]">
        <span className="text-zinc-500 dark:text-zinc-400 font-medium">
          Força da senha:
        </span>
        <span
          className={`font-semibold ${
            score === 0
              ? "text-red-500"
              : score === 1
                ? "text-amber-500"
                : score === 2
                  ? "text-yellow-600 dark:text-yellow-400"
                  : "text-emerald-600 dark:text-emerald-400"
          }`}
        >
          {label}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-1 h-1.5 w-full bg-zinc-100 dark:bg-zinc-800/80 rounded-full overflow-hidden p-0.5">
        {[1, 2, 3, 4].map((step) => {
          const isActive = score >= step;
          return (
            <div
              key={step}
              className={`h-full rounded-full transition-all duration-300 ${
                isActive ? colorClass : "bg-transparent"
              }`}
            />
          );
        })}
      </div>

      {feedback && score < 3 && (
        <p className="text-[10px] text-zinc-400 dark:text-zinc-500 leading-tight">
          {feedback}
        </p>
      )}
    </div>
  );
}
