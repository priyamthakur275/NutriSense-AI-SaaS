import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

const meals = [
  { name: "Vegetable Thali", time: "12:40 PM", location: "Hostel Block A", compliance: 94, tone: "success" as const },
  { name: "Rice & Dal Combo", time: "12:22 PM", location: "Main Canteen", compliance: 88, tone: "success" as const },
  { name: "Paneer Curry Set", time: "12:05 PM", location: "Hostel Block C", compliance: 71, tone: "warning" as const },
  { name: "Chapati & Sabzi", time: "11:48 AM", location: "Staff Canteen", compliance: 65, tone: "destructive" as const },
];

export function RecentMealsCard() {
  return (
    <Card className="p-6">
      <CardHeader className="flex-row items-center justify-between space-y-0 p-0 pb-4">
        <div>
          <CardTitle>Recent Meals</CardTitle>
          <CardDescription>Latest tray analyses across your institution</CardDescription>
        </div>
        <button className="flex items-center gap-1 text-xs font-medium text-primary hover:underline">
          View all <ArrowUpRight size={12} />
        </button>
      </CardHeader>
      <CardContent className="flex flex-col gap-1 p-0">
        {meals.map((meal, i) => (
          <motion.div
            key={meal.name}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: i * 0.06 }}
            className="flex items-center justify-between gap-3 rounded-lg px-2 py-2.5 transition-colors hover:bg-secondary/50"
          >
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">{meal.name}</p>
              <p className="text-xs text-muted-foreground">
                {meal.location} · {meal.time}
              </p>
            </div>
            <Badge variant={meal.tone}>{meal.compliance}%</Badge>
          </motion.div>
        ))}
      </CardContent>
    </Card>
  );
}
