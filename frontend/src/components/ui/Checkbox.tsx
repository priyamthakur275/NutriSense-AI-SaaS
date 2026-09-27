import * as React from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CheckboxProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, id, checked, ...props }, ref) => {
    return (
      <label
        htmlFor={id}
        className={cn("inline-flex select-none items-center gap-2 text-sm text-muted-foreground", className)}
      >
        <span className="relative inline-flex h-4.5 w-4.5 flex-shrink-0">
          <input
            id={id}
            ref={ref}
            type="checkbox"
            checked={checked}
            className="peer absolute inset-0 h-full w-full cursor-pointer appearance-none rounded-[5px] border border-border bg-background transition-colors checked:border-primary checked:bg-primary"
            {...props}
          />
          <Check
            size={12}
            strokeWidth={3}
            className={cn(
              "pointer-events-none absolute inset-0 m-auto text-primary-foreground opacity-0 transition-opacity",
              "peer-checked:opacity-100"
            )}
          />
        </span>
        {label && <span>{label}</span>}
      </label>
    );
  }
);
Checkbox.displayName = "Checkbox";
