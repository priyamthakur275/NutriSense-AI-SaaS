import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Info, CheckCircle2, AlertTriangle, XCircle, X } from "lucide-react";
import { cn } from "@/lib/utils";

const alertVariants = cva(
  "relative flex w-full items-start gap-3 rounded-xl border p-4 text-sm",
  {
    variants: {
      variant: {
        info: "border-blue-500/20 bg-blue-500/[0.06] text-blue-700 dark:text-blue-300",
        success:
          "border-emerald-500/20 bg-emerald-500/[0.06] text-emerald-700 dark:text-emerald-300",
        warning:
          "border-amber-500/20 bg-amber-500/[0.06] text-amber-700 dark:text-amber-300",
        destructive: "border-red-500/20 bg-red-500/[0.06] text-red-700 dark:text-red-300",
      },
    },
    defaultVariants: { variant: "info" },
  }
);

const iconMap = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  destructive: XCircle,
};

export interface AlertProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {
  title?: string;
  onDismiss?: () => void;
}

export function Alert({
  className,
  variant = "info",
  title,
  children,
  onDismiss,
  ...props
}: AlertProps) {
  const Icon = iconMap[variant ?? "info"];

  return (
    <div className={cn(alertVariants({ variant }), className)} {...props}>
      <Icon size={17} className="mt-0.5 flex-shrink-0" />
      <div className="min-w-0 flex-1">
        {title && <p className="font-medium text-foreground">{title}</p>}
        {children && <div className={cn("text-foreground/80", title && "mt-0.5")}>{children}</div>}
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          aria-label="Dismiss"
          className="flex-shrink-0 rounded-md p-0.5 text-current opacity-60 transition-opacity hover:opacity-100"
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
}
