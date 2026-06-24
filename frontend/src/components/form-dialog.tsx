import { type ReactNode } from "react";
import { type UseFormReturn } from "react-hook-form";
import { Loader2 } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";

interface FormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- UseFormReturn is invariant in practice
  form: UseFormReturn<any>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void> | void;
  isPending: boolean;
  submitLabel: string;
  children: ReactNode;
  maxWidth?: string;
  submitDisabled?: boolean;
}

const MAX_WIDTH_MAP: Record<string, string> = {
  "425px": "sm:max-w-[425px]",
  "480px": "sm:max-w-[480px]",
  "520px": "sm:max-w-[520px]",
  "560px": "sm:max-w-[560px]",
  "600px": "sm:max-w-[600px]",
};

export function FormDialog({
  open,
  onOpenChange,
  title,
  description,
  form,
  onSubmit,
  isPending,
  submitLabel,
  children,
  maxWidth = "560px",
  submitDisabled,
}: FormDialogProps) {
  const disabled = submitDisabled ?? isPending;
  const contentClass = MAX_WIDTH_MAP[maxWidth] ?? "sm:max-w-[560px]";
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={contentClass}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description ? (
            <DialogDescription>{description}</DialogDescription>
          ) : (
            <DialogDescription className="sr-only">
              Formulário para {title.toLowerCase()}
            </DialogDescription>
          )}
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={onSubmit} className="space-y-4">
            {children}

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={disabled}>
                {isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
                {submitLabel}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
