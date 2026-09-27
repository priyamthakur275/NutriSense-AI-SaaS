import { motion } from "framer-motion";
import { AlertTriangle, TrendingDown, Clock } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

const alerts = [
  {
    icon: TrendingDown,
    title: "Iron deficit — 3rd consecutive day",
    tone: "destructive" as const,
    due: "Review today",
  },
  {
    icon: AlertTriangle,
    title: "Hostel Block C below 80% compliance",
    tone: "warning" as const,
    due: "Review by tomorrow",
  },
  {
    icon: Clock,
    title: "Weekly menu plan needs approval",
    tone: "warning" as const,
    due: "Due in 2 days",
  },
];

export function UpcomingAlertsCard() {
  return (
    <Card className="p-6">
      <CardHeader className="p-0 pb-4">
        <CardTitle>Upcoming Alerts</CardTitle>
        <CardDescription>Items that need your attention</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-2 p-0">
        {alerts.map((alert, i) => (
          <motion.div
            key={alert.title}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.07 }}
            className="flex items-start gap-3 rounded-lg border border-border p-3"
          >
            <span
              className={
                "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg " +
                (alert.tone === "destructive"
                  ? "bg-red-500/10 text-red-600 dark:text-red-400"
                  : "bg-amber-500/10 text-amber-600 dark:text-amber-400")
              }
            >
              <alert.icon size={15} />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium leading-snug">{alert.title}</p>
              <Badge variant={alert.tone} className="mt-1.5">
                {alert.due}
              </Badge>
            </div>
          </motion.div>
        ))}
      </CardContent>
    </Card>
  );
}
