import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus, type LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { AnimatedCounter } from "@/components/landing/AnimatedCounter";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: number;
  suffix?: string;
  decimals?: number;
  icon: LucideIcon;
  trend?: "up" | "down" | "flat";
  trendLabel?: string;
  delay?: number;
  className?: string;
}

const trendConfig = {
  up: { icon: TrendingUp, className: "text-emerald-500" },
  down: { icon: TrendingDown, className: "text-red-500" },
  flat: { icon: Minus, className: "text-muted-foreground" },
};

export function StatCard({
  label,
  value,
  suffix = "",
  decimals = 0,
  icon: Icon,
  trend,
  trendLabel,
  delay = 0,
  className,
}: StatCardProps) {
  const TrendIcon = trend ? trendConfig[trend].icon : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay }}
    >
      <Card className={cn("p-5 relative overflow-hidden group hover:-translate-y-1 hover:shadow-lg transition-all duration-300", className)}>
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">{label}</p>
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-accent-foreground">
            <Icon size={15} />
          </span>
        </div>
        <div className="mt-2 flex items-end justify-between">
          <AnimatedCounter
            value={value}
            suffix={suffix}
            decimals={decimals}
            className="text-2xl font-bold tabular-nums"
          />
          {trend && TrendIcon && (
            <span className={cn("flex items-center gap-1 text-xs font-medium", trendConfig[trend].className)}>
              <TrendIcon size={13} />
              {trendLabel}
            </span>
          )}
        </div>
      </Card>
    </motion.div>
  );
}
