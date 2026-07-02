import { Eye, EyeOff } from "lucide-react";
import { forwardRef, useState } from "react";
import { Input } from "@/components/ui/input";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface PasswordInputProps {
  id?: string;
  placeholder: string;
  className?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  name?: string;
}

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  function PasswordInput({ id, placeholder, className = "", ...props }, ref) {
    const [visible, setVisible] = useState(false);

    return (
      <div className="relative">
        <Input
          id={id}
          ref={ref}
          type={visible ? "text" : "password"}
          className={`pr-10 text-xs border-zinc-200 dark:border-zinc-850 bg-zinc-50 dark:bg-zinc-900 rounded-xl placeholder-zinc-400 focus-visible:ring-aura-500/30 focus-visible:border-aura-500 font-medium ${className}`}
          placeholder={placeholder}
          {...props}
        />
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              type="button"
              onClick={() => setVisible(!visible)}
              className="absolute right-3 top-1/2 -translate-y-1/2 h-7 w-7 flex items-center justify-center text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors focus-visible:ring-2 focus-visible:ring-aura-500 outline-none rounded-sm"
              aria-label={visible ? "Ocultar senha" : "Mostrar senha"}
            >
              {visible ? (
                <EyeOff className="w-4 h-4" />
              ) : (
                <Eye className="w-4 h-4" />
              )}
            </button>
          </TooltipTrigger>
          <TooltipContent side="top" align="center">
            {visible ? "Ocultar senha" : "Mostrar senha"}
          </TooltipContent>
        </Tooltip>
      </div>
    );
  },
);
