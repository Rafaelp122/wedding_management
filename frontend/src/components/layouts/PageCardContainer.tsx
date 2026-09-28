import React from "react";
import { cn } from "@/lib/utils";

export interface PageCardContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function PageCardContainer({
  children,
  className,
  ...props
}: PageCardContainerProps) {
  return (
    <div
      className={cn(
        "bg-card rounded-xl border border-border shadow-soft overflow-hidden",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
