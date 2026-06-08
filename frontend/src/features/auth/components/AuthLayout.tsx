import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";

interface AuthLayoutProps {
  children: ReactNode;
  heroQuote: string;
  heroBadgeLabel: string;
  heroBoxTitle: string;
  heroBoxSubtitle: string;
  heroBoxBadge: string;
  heroBoxLeftLabel: string;
  heroBoxLeftValue: string;
  heroBoxRightLabel: string;
  heroBoxRightValue: string;
}

export function AuthLayout({
  children,
  heroQuote,
  heroBadgeLabel,
  heroBoxTitle,
  heroBoxSubtitle,
  heroBoxBadge,
  heroBoxLeftLabel,
  heroBoxLeftValue,
  heroBoxRightLabel,
  heroBoxRightValue,
}: AuthLayoutProps) {
  const { theme, setTheme } = useTheme();

  return (
    <div className="bg-surface-light dark:bg-surface-dark text-zinc-900 dark:text-zinc-50 font-sans transition-colors duration-300 h-screen overflow-hidden flex flex-col justify-between">
      <header className="absolute top-0 inset-x-0 h-20 px-8 flex items-center justify-between z-30">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-aura-600 flex items-center justify-center shadow-glow">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 22v-7l-2-2a4 4 0 1 1 4 0l-2 2v7" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <span className="font-display font-bold text-lg tracking-tight text-zinc-950 dark:text-white">
            Aura ERP
          </span>
        </Link>

        <div className="flex items-center gap-2.5">
          <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 dark:text-zinc-500 hidden sm:block">
            Foco Visual
          </span>
          <button
            type="button"
            onClick={() =>
              setTheme(theme === "dark" ? "light" : "dark")
            }
            className="group relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full bg-zinc-200 dark:bg-zinc-800 transition-colors duration-300 focus:outline-none"
            role="switch"
            aria-checked={theme === "dark"}
          >
            <span
              className={`pointer-events-none inline-flex h-5 w-5 items-center justify-center rounded-full bg-white dark:bg-zinc-950 shadow-md transition-transform duration-300 text-[10px] ${theme === "dark" ? "translate-x-5" : "translate-x-1"}`}
            >
              {theme === "dark" ? (
                <Moon className="w-3 h-3" />
              ) : (
                <Sun className="w-3 h-3" />
              )}
            </span>
          </button>
        </div>
      </header>

      <div className="flex-1 w-full grid grid-cols-1 lg:grid-cols-12 min-h-0">
        <div className="lg:col-span-5 flex flex-col justify-center px-8 sm:px-16 lg:px-20 py-24 bg-white dark:bg-surface-dark transition-colors duration-300 z-10 overflow-y-auto">
          {children}
        </div>

        <div className="hidden lg:flex lg:col-span-7 h-full bg-[#FAF9FC] dark:bg-zinc-950 border-l border-zinc-200/50 dark:border-zinc-900/60 flex-col justify-between p-12 relative overflow-hidden transition-colors duration-300">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(124,58,237,0.04),transparent_60%)] pointer-events-none" />
          <div className="absolute right-[-20%] top-[-20%] w-[80%] h-[80%] bg-aura-500/5 rounded-full blur-[120px] pointer-events-none" />

          <div className="w-full" />

          <div className="max-w-xl mx-auto space-y-10 relative z-10">
            <div className="space-y-4">
              <span className="text-xs font-bold text-aura-600 dark:text-aura-500 uppercase tracking-widest block font-mono">
                {heroBadgeLabel}
              </span>
              <h2 className="font-serif italic text-3xl xl:text-4xl text-zinc-900 dark:text-white leading-tight font-medium">
                {heroQuote}
              </h2>
            </div>

            <div className="bg-white/80 dark:bg-white/5 backdrop-blur-md rounded-2xl border border-zinc-200 dark:border-white/10 p-5 space-y-4 shadow-2xl relative overflow-hidden text-left transition-colors duration-300">
              <div className="absolute right-0 top-0 w-16 h-16 bg-aura-500/5 rounded-bl-full" />

              <div className="flex items-center justify-between border-b border-zinc-200 dark:border-white/10 pb-3">
                <div>
                  <h4 className="font-display font-bold text-sm text-zinc-900 dark:text-white">
                    {heroBoxTitle}
                  </h4>
                  <p className="text-[10px] text-zinc-400">
                    {heroBoxSubtitle}
                  </p>
                </div>
                <span className="bg-aura-500/10 text-aura-600 dark:text-aura-400 text-[10px] px-2.5 py-0.5 rounded-full font-bold">
                  {heroBoxBadge}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-zinc-50 dark:bg-white/5 p-2.5 rounded-lg border border-zinc-100 dark:border-white/5">
                  <span className="text-[8px] font-bold text-zinc-450 uppercase tracking-wider block">
                    {heroBoxLeftLabel}
                  </span>
                  <span className="font-mono text-xs font-bold text-zinc-900 dark:text-white">
                    {heroBoxLeftValue}
                  </span>
                </div>
                <div className="bg-zinc-50 dark:bg-white/5 p-2.5 rounded-lg border border-zinc-100 dark:border-white/5">
                  <span className="text-[8px] font-bold text-zinc-455 uppercase tracking-wider block">
                    {heroBoxRightLabel}
                  </span>
                  <span className="font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">
                    {heroBoxRightValue}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="w-full flex items-center justify-between text-[10px] text-zinc-450 dark:text-zinc-500 relative z-10">
            <span>
              © 2026 Aura Inc. Todos os direitos reservados.
            </span>
            <span className="font-mono text-[9px] uppercase tracking-wider">
              Aura Core v1.2
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
