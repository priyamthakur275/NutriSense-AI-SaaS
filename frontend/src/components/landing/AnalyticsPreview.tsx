import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { SectionHeading } from "@/components/landing/SectionHeading";
import { Card } from "@/components/ui/Card";
import { AnimatedCounter } from "@/components/landing/AnimatedCounter";

const kpis = [
  { label: "Avg. Compliance", value: 92.4, suffix: "%", trend: "up", decimals: 1 },
  { label: "Meals / Day", value: 1284, suffix: "", trend: "up" },
  { label: "Nutrient Gaps", value: 6, suffix: "", trend: "down" },
  { label: "Active Institutions", value: 41, suffix: "", trend: "flat" },
];

const nutrients = [
  { label: "Protein", value: 82 },
  { label: "Iron", value: 61 },
  { label: "Calcium", value: 74 },
  { label: "Vitamin C", value: 88 },
  { label: "Fiber", value: 55 },
];

const heat = Array.from({ length: 28 }, () => Math.round(30 + Math.random() * 70));

function trendIcon(trend: string) {
  if (trend === "up") return <TrendingUp size={14} className="text-emerald-500" />;
  if (trend === "down") return <TrendingDown size={14} className="text-red-500" />;
  return <Minus size={14} className="text-muted-foreground" />;
}

export function AnalyticsPreview() {
  return (
    <section id="analytics" className="px-6 py-24">
      <div className="mx-auto max-w-7xl">
        <SectionHeading
          eyebrow="Analytics"
          title="Data that drives decisions"
          description="Every meal becomes a data point — trends, gaps, and forecasts, always up to date."
        />

        <div className="mt-14 grid grid-cols-2 gap-4 md:grid-cols-4">
          {kpis.map((kpi, i) => (
            <motion.div
              key={kpi.label}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
            >
              <Card className="p-5">
                <p className="text-xs text-muted-foreground">{kpi.label}</p>
                <div className="mt-1.5 flex items-center gap-1.5">
                  <AnimatedCounter
                    value={kpi.value}
                    suffix={kpi.suffix}
                    decimals={kpi.decimals ?? 0}
                    className="text-2xl font-bold tabular-nums"
                  />
                  {trendIcon(kpi.trend)}
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Nutrient progress bars */}
          <Card className="p-6 lg:col-span-1">
            <h3 className="text-sm font-semibold">Nutrient Coverage</h3>
            <div className="mt-5 space-y-4">
              {nutrients.map((n, i) => (
                <div key={n.label}>
                  <div className="mb-1 flex justify-between text-xs">
                    <span className="text-muted-foreground">{n.label}</span>
                    <span className="font-medium">{n.value}%</span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: `${n.value}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.8, delay: i * 0.08, ease: "easeOut" }}
                      className="h-full rounded-full bg-primary"
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Trend chart */}
          <Card className="p-6 lg:col-span-1">
            <h3 className="text-sm font-semibold">Compliance Trend</h3>
            <div className="mt-6 flex h-40 items-end gap-1.5">
              {[58, 64, 61, 70, 68, 75, 79, 74, 82, 85, 88, 92].map((h, i) => (
                <motion.div
                  key={i}
                  initial={{ height: 0 }}
                  whileInView={{ height: `${h}%` }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.04, ease: "easeOut" }}
                  className="flex-1 rounded-t-sm bg-gradient-to-t from-primary/70 to-primary/20"
                />
              ))}
            </div>
            <p className="mt-3 text-xs text-muted-foreground">Last 12 weeks, institution average</p>
          </Card>

          {/* Heatmap */}
          <Card className="p-6 lg:col-span-1">
            <h3 className="text-sm font-semibold">Nutrition Heatmap</h3>
            <p className="mt-1 text-xs text-muted-foreground">Daily compliance intensity — last 4 weeks</p>
            <div className="mt-5 grid grid-cols-7 gap-1.5">
              {heat.map((v, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.5 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: idx * 0.012 }}
                  className="aspect-square rounded-sm"
                  style={{
                    backgroundColor: `hsl(var(--primary) / ${(v / 100) * 0.9 + 0.08})`,
                  }}
                  title={`${v}% compliance`}
                />
              ))}
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
