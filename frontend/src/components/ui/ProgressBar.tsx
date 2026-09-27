import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number;
  label?: string;
  valueLabel?: string;
  className?: string;
  barClassName?: string;
  delay?: number;
}

export function ProgressBar({
  value,
  label,
  valueLabel,
  className,
  barClassName,
  delay = 0,
}: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div className={cn("w-full", className)}>
      {(label || valueLabel) && (
        <div className="mb-1.5 flex items-center justify-between text-xs">
          {label && <span className="text-muted-foreground">{label}</span>}
          {valueLabel && <span className="font-medium">{valueLabel}</span>}
        </div>
      )}
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${clamped}%` }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay, ease: "easeOut" }}
          className={cn("h-full rounded-full bg-primary", barClassName)}
        />
      </div>
    </div>
  );
}
