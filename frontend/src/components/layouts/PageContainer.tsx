import React from "react";
import { cn } from "@/lib/utils";

export interface PageContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function PageContainer({ children, className, ...props }: PageContainerProps) {
  return (
    <div
      className={cn(
        "max-w-7xl mx-auto space-y-6 animate-in fade-in duration-300",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
