import { Eye, EyeOff } from "lucide-react";
import { forwardRef, useState } from "react";

interface PasswordInputProps {
  id: string;
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
        <input
          id={id}
          ref={ref}
          type={visible ? "text" : "password"}
          className={`block w-full pl-3.5 pr-10 py-2.5 text-xs border border-zinc-200 dark:border-zinc-850 bg-zinc-50 dark:bg-zinc-900 rounded-xl text-zinc-955 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-aura-500/30 focus:border-aura-500 transition-all font-medium ${className}`}
          placeholder={placeholder}
          {...props}
        />
        <button
          type="button"
          onClick={() => setVisible(!visible)}
          className="absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors"
          tabIndex={-1}
        >
          {visible ? (
            <EyeOff className="w-4 h-4" />
          ) : (
            <Eye className="w-4 h-4" />
          )}
        </button>
      </div>
    );
  },
);
