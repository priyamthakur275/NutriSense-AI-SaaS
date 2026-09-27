import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { useAuthStore } from "@/store/authStore";

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export function WelcomeCard() {
  const user = useAuthStore((s) => s.user);
  const firstName = user?.fullName?.split(" ")[0] ?? "there";

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="relative overflow-hidden p-6 md:p-7">
        <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-primary/10 blur-3xl" />
        <div className="relative flex flex-col gap-1">
          <span className="inline-flex w-fit items-center gap-1.5 rounded-full border border-primary/20 bg-primary/[0.06] px-2.5 py-1 text-xs font-medium text-primary">
            <Sparkles size={12} /> Daily summary ready
          </span>
          <h1 className="mt-2 text-2xl font-bold tracking-tight md:text-3xl">
            {getGreeting()}, {firstName} 👋
          </h1>
          <p className="mt-1 max-w-xl text-sm text-muted-foreground md:text-base">
            Here's how your institution's nutrition compliance is trending today.
            Everything looks on track — one recommendation needs your attention.
          </p>
        </div>
      </Card>
    </motion.div>
  );
}
