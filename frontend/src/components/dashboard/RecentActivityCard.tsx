import { motion } from "framer-motion";
import { Camera, UserCheck, FileBarChart, Bot } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";

const activity = [
  { icon: Camera, text: "Tray scanned at Main Canteen", time: "2 min ago" },
  { icon: UserCheck, text: "142 students marked present for lunch", time: "18 min ago" },
  { icon: Bot, text: "Suggestion Agent flagged iron deficit", time: "1h ago" },
  { icon: FileBarChart, text: "Weekly compliance report generated", time: "3h ago" },
  { icon: Camera, text: "Tray scanned at Hostel Block C", time: "4h ago" },
];

export function RecentActivityCard() {
  return (
    <Card className="p-6">
      <CardHeader className="p-0 pb-4">
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>System events across the platform</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <div className="relative flex flex-col gap-5 pl-1">
          <div className="absolute bottom-2 left-[13px] top-2 w-px bg-border" />
          {activity.map((item, i) => (
            <motion.div
              key={item.text + i}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: i * 0.06 }}
              className="relative flex items-start gap-3"
            >
              <span className="relative z-10 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border border-border bg-card text-muted-foreground">
                <item.icon size={13} />
              </span>
              <div className="min-w-0 pt-0.5">
                <p className="text-sm text-foreground/90">{item.text}</p>
                <p className="text-xs text-muted-foreground">{item.time}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
