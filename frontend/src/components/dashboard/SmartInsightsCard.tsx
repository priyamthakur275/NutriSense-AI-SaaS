import { motion } from "framer-motion";
import { Lightbulb, ArrowUpRight, ArrowDownRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";

const insights = [
  {
    text: "Protein compliance improved 6% week-over-week after the menu adjustment.",
    trend: "up" as const,
  },
  {
    text: "Attendance at breakfast has dropped 9% at Hostel Block B this month.",
    trend: "down" as const,
  },
  {
    text: "Vitamin C coverage is consistently strongest on days citrus fruit is served.",
    trend: "up" as const,
  },
];

export function SmartInsightsCard() {
  return (
    <Card className="p-6">
      <CardHeader className="flex-row items-center gap-2 space-y-0 p-0 pb-4">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-accent-foreground">
          <Lightbulb size={15} />
        </span>
        <div>
          <CardTitle>Smart Insights</CardTitle>
          <CardDescription>Patterns surfaced from your data</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 p-0">
        {insights.map((insight, i) => (
          <motion.div
            key={insight.text}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.07 }}
            className="flex items-start gap-2.5 rounded-lg bg-secondary/40 p-3"
          >
            {insight.trend === "up" ? (
              <ArrowUpRight size={15} className="mt-0.5 flex-shrink-0 text-emerald-500" />
            ) : (
              <ArrowDownRight size={15} className="mt-0.5 flex-shrink-0 text-red-500" />
            )}
            <p className="text-sm leading-relaxed text-foreground/85">{insight.text}</p>
          </motion.div>
        ))}
      </CardContent>
    </Card>
  );
}
