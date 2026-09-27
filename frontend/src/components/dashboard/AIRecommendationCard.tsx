import { motion } from "framer-motion";
import { Bot, ArrowRight, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export function AIRecommendationCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="relative overflow-hidden border-primary/20 bg-gradient-to-br from-primary/[0.06] to-transparent p-6">
        <div className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-primary/10 blur-3xl" />
        <div className="relative flex items-start gap-3">
          <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
            <Bot size={18} />
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5">
              <p className="text-sm font-semibold">Recommendation Agent</p>
              <Sparkles size={12} className="text-primary" />
            </div>
            <p className="mt-1.5 text-sm leading-relaxed text-foreground/85">
              Iron intake has been below target for 3 consecutive days across
              Hostel Block C. Consider adding leafy greens or fortified cereal
              to tomorrow's dinner menu to close the gap.
            </p>
            <Button size="sm" variant="outline" className="mt-4 border-primary/30">
              Review menu plan <ArrowRight size={13} />
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
