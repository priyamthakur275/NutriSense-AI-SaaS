import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ProgressRing } from "@/components/dashboard/ProgressRing";
import { cn } from "@/lib/utils";

interface ScoreCardProps {
  title: string;
  score: number;
  description: string;
  icon: LucideIcon;
  status: "success" | "warning" | "destructive";
  statusLabel: string;
  delay?: number;
}

const ringToneClass: Record<ScoreCardProps["status"], string> = {
  success: "stroke-emerald-500",
  warning: "stroke-amber-500",
  destructive: "stroke-red-500",
};

export function ScoreCard({
  title,
  score,
  description,
  icon: Icon,
  status,
  statusLabel,
  delay = 0,
}: ScoreCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay }}
    >
      <Card className="flex items-center gap-5 p-5">
        <ProgressRing value={score} size={72} strokeWidth={7} className={cn(ringToneClass[status])}>
          <span className="text-sm font-bold">{score}%</span>
        </ProgressRing>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <Icon size={15} className="text-muted-foreground" />
            <p className="text-sm font-semibold">{title}</p>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">{description}</p>
          <Badge variant={status} className="mt-2">
            {statusLabel}
          </Badge>
        </div>
      </Card>
    </motion.div>
  );
}
