import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Monitor, Smartphone, Camera, ShieldCheck } from "lucide-react";
import { SectionHeading } from "@/components/landing/SectionHeading";
import { cn } from "@/lib/utils";

const tabs = [
  {
    id: "dashboard",
    label: "Dashboard",
    icon: Monitor,
    description: "Institution-wide compliance and nutrition trends at a glance.",
  },
  {
    id: "mobile",
    label: "Mobile",
    icon: Smartphone,
    description: "Staff capture trays and check status from any device.",
  },
  {
    id: "camera",
    label: "Camera Capture",
    icon: Camera,
    description: "Live tray recognition with bounding-box confidence scores.",
  },
  {
    id: "nutrition",
    label: "Nutrition Analysis",
    icon: ShieldCheck,
    description: "Full macro/micronutrient breakdown scored against standards.",
  },
];

export function ProductDemo() {
  const [active, setActive] = useState("dashboard");
  const activeTab = tabs.find((t) => t.id === active)!;

  return (
    <section className="px-6 py-24">
      <div className="mx-auto max-w-7xl">
        <SectionHeading
          eyebrow="Product Demo"
          title="See NutriSense AI in action"
          description="One platform, every surface — desktop dashboards, mobile capture, and live camera recognition."
        />

        <div className="mt-12 flex flex-wrap items-center justify-center gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActive(tab.id)}
              className={cn(
                "relative flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors",
                active === tab.id
                  ? "text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {active === tab.id && (
                <motion.span
                  layoutId="demo-tab-pill"
                  className="absolute inset-0 -z-10 rounded-full bg-primary"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.5 }}
                />
              )}
              <tab.icon size={15} />
              {tab.label}
            </button>
          ))}
        </div>

        <div className="mt-10">
          <AnimatePresence mode="wait">
            <motion.div
              key={active}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.35 }}
              className="glow mx-auto max-w-4xl overflow-hidden rounded-2xl border border-border bg-card"
            >
              <div className="flex items-center justify-between border-b border-border bg-secondary/40 px-5 py-3">
                <div className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
                  <span className="h-2.5 w-2.5 rounded-full bg-yellow-400" />
                  <span className="h-2.5 w-2.5 rounded-full bg-green-400" />
                </div>
                <p className="text-xs text-muted-foreground">{activeTab.description}</p>
                <span className="w-14" />
              </div>

              <div className="flex min-h-[22rem] items-center justify-center bg-gradient-to-br from-secondary/40 to-transparent p-10">
                <DemoVisual id={active} />
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}

function DemoVisual({ id }: { id: string }) {
  if (id === "mobile") {
    return (
      <div className="mx-auto flex h-80 w-44 flex-col rounded-[2rem] border-4 border-secondary bg-background p-3 shadow-xl">
        <div className="mx-auto mb-3 h-1.5 w-10 rounded-full bg-secondary" />
        <div className="flex-1 space-y-2 overflow-hidden rounded-xl bg-secondary/40 p-2">
          <div className="h-16 rounded-lg bg-primary/20" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-8 rounded-lg bg-background" />
          ))}
        </div>
      </div>
    );
  }

  if (id === "camera") {
    return (
      <div className="relative w-full max-w-md">
        <div className="aspect-video w-full rounded-xl border-2 border-dashed border-primary/40 bg-secondary/30" />
        {[
          { top: "20%", left: "15%", w: "30%", h: "35%" },
          { top: "45%", left: "55%", w: "28%", h: "30%" },
        ].map((box, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 + i * 0.2 }}
            style={{ top: box.top, left: box.left, width: box.w, height: box.h }}
            className="absolute rounded-md border-2 border-primary"
          >
            <span className="absolute -top-6 left-0 rounded bg-primary px-1.5 py-0.5 text-[10px] font-medium text-primary-foreground">
              {i === 0 ? "Rice · 96%" : "Dal · 91%"}
            </span>
          </motion.div>
        ))}
      </div>
    );
  }

  if (id === "nutrition") {
    return (
      <div className="grid w-full max-w-md grid-cols-2 gap-3">
        {[
          { label: "Calories", value: "612 kcal" },
          { label: "Protein", value: "24g" },
          { label: "Carbs", value: "78g" },
          { label: "Fat", value: "18g" },
        ].map((n) => (
          <div key={n.label} className="rounded-xl border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">{n.label}</p>
            <p className="mt-1 text-lg font-bold">{n.value}</p>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid w-full max-w-lg grid-cols-3 gap-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "rounded-lg bg-secondary/60",
            i === 0 ? "col-span-2 row-span-2 h-32" : "h-16"
          )}
        />
      ))}
    </div>
  );
}
