import { motion } from "framer-motion";
import { Flame, Beef, Wheat, Droplets, GlassWater } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { ProgressRing } from "@/components/dashboard/ProgressRing";

const nutrients = [
  { label: "Calories", value: 1840, target: 2200, unit: "kcal", icon: Flame, pct: 84 },
  { label: "Protein", value: 62, target: 80, unit: "g", icon: Beef, pct: 78 },
  { label: "Carbs", value: 210, target: 260, unit: "g", icon: Wheat, pct: 81 },
  { label: "Fat", value: 48, target: 65, unit: "g", icon: Droplets, pct: 74 },
  { label: "Hydration", value: 1.6, target: 2.5, unit: "L", icon: GlassWater, pct: 64 },
];

export function NutritionSummaryCard() {
  return (
    <Card className="p-6">
      <CardHeader className="p-0 pb-5">
        <CardTitle>Today's Nutrition</CardTitle>
        <CardDescription>Aggregated across all logged meals today</CardDescription>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-5 p-0 sm:grid-cols-3 lg:grid-cols-5">
        {nutrients.map((n, i) => (
          <motion.div
            key={n.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: i * 0.06 }}
            className="flex flex-col items-center gap-2 text-center"
          >
            <ProgressRing value={n.pct} size={76} strokeWidth={6}>
              <n.icon size={18} className="text-primary" />
            </ProgressRing>
            <div>
              <p className="text-sm font-semibold">
                {n.value}
                <span className="text-xs font-normal text-muted-foreground">/{n.target}{n.unit}</span>
              </p>
              <p className="text-xs text-muted-foreground">{n.label}</p>
            </div>
          </motion.div>
        ))}
      </CardContent>
    </Card>
  );
}
