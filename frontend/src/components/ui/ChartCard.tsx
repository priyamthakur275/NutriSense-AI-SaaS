import { motion } from "framer-motion";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface ChartCardProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  legend?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export function ChartCard({
  title,
  description,
  action,
  legend,
  children,
  className,
  delay = 0,
}: ChartCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className={className}
    >
      <Card className="p-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold">{title}</h3>
            {description && (
              <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
            )}
          </div>
          {action}
        </div>
        <div className={cn("mt-4", legend && "mb-2")}>{children}</div>
        {legend && <div className="mt-3 flex flex-wrap gap-4">{legend}</div>}
      </Card>
    </motion.div>
  );
}

export function ChartLegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
      <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
      {label}
    </div>
  );
}
