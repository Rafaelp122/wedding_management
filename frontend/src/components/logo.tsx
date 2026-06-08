import type { AnchorHTMLAttributes } from "react";

export const RingsIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="9" cy="13" r="5.5" />
    <circle cx="15" cy="11" r="5.5" />
  </svg>
);

interface LogoProps {
  /** Renders as a link. Omit for a plain div (sidebar). */
  href?: string;
  className?: string;
  iconClassName?: string;
  textClassName?: string;
  /** Props forwarded to the anchor element when href is set. */
  linkProps?: AnchorHTMLAttributes<HTMLAnchorElement>;
}

export function Logo({
  href,
  className = "",
  iconClassName = "size-8",
  textClassName = "font-bold text-xl tracking-tight text-zinc-900 dark:text-white ml-3 truncate font-display",
  linkProps,
}: LogoProps) {
  const icon = (
    <div
      className={`${iconClassName} rounded-lg bg-primary flex items-center justify-center shadow-[0_0_15px_rgba(124,58,237,0.3)] shrink-0`}
    >
      <RingsIcon className="size-[18px] text-primary-foreground" />
    </div>
  );

  const text = (
    <span className={textClassName}>Sim, Aceito!</span>
  );

  const content = (
    <div className={`flex items-center ${className}`}>
      {icon}
      {text}
    </div>
  );

  if (href) {
    return (
      <a href={href} {...linkProps}>
        {content}
      </a>
    );
  }

  return content;
}
