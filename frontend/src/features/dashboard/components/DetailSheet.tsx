import { type ReactNode } from "react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface DetailSheetProps {
  trigger: ReactNode;
  title: string;
  description: string;
  icon: LucideIcon;
  iconColor: string;
  isLoading: boolean;
  isEmpty: boolean;
  emptyMessage: string;
  children: ReactNode;
}

export function DetailSheet({
  trigger,
  title,
  description,
  icon: Icon,
  iconColor,
  isLoading,
  isEmpty,
  emptyMessage,
  children,
}: DetailSheetProps) {
  return (
    <Sheet>
      <SheetTrigger asChild>{trigger}</SheetTrigger>
      <SheetContent
        side="right"
        className="sm:max-w-md bg-background"
      >
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <Icon className={cn("size-5", iconColor)} />
            {title}
          </SheetTitle>
          <SheetDescription>{description}</SheetDescription>
        </SheetHeader>
        <div className="mt-6 space-y-3">
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-lg" />
              ))}
            </div>
          ) : isEmpty ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              {emptyMessage}
            </p>
          ) : (
            children
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
