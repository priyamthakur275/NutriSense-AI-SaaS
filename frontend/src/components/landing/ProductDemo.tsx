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
          title="The same scan, on every screen"
          description="Kitchen staff capture on a phone, managers review on a laptop."
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
                <p className="text-sm text-muted-foreground">{activeTab.description}</p>
              </div>

              <div className="flex min-h-[22rem] items-center justify-center p-8 md:p-12">
                <DemoVisual id={active} />
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}

const week = [
  { d: "Mon", v: 78 }, { d: "Tue", v: 84 }, { d: "Wed", v: 71 }, { d: "Thu", v: 88 },
  { d: "Fri", v: 82 }, { d: "Sat", v: 64 }, { d: "Sun", v: 90 },
];

function DemoVisual({ id }: { id: string }) {
  if (id === "mobile") {
    return (
      <div className="mx-auto w-56 rounded-[2.2rem] bg-sidebar p-2.5 shadow-2xl">
        <div className="overflow-hidden rounded-[1.75rem] bg-background">
          <div className="mx-auto mt-2 h-1.5 w-14 rounded-full bg-steel" />
          <div className="p-4">
            <p className="text-xs text-muted-foreground">Dinner, 8:12 pm</p>
            <p className="font-display mt-1 text-lg font-bold leading-tight">Tray scanned</p>
            <div className="mt-3 aspect-[4/3] rounded-xl bg-[#DDE3DF] p-2">
              <div className="grid h-full grid-cols-3 grid-rows-2 gap-1.5">
                <div className="row-span-2 rounded-lg bg-[#F4EFE2] ring-2 ring-primary" />
                <div className="rounded-lg bg-[#E0A21F] ring-2 ring-primary" />
                <div className="rounded-lg bg-[#E8C35A] ring-2 ring-primary" />
                <div className="rounded-lg bg-[#D9A866] ring-2 ring-primary" />
                <div className="rounded-lg bg-[#FBFAF5] ring-2 ring-primary" />
              </div>
            </div>
            <ul className="mt-3 space-y-1.5 text-[13px]">
              {[["Energy", "642 kcal"], ["Protein", "19 g"], ["Iron", "3.1 mg"]].map(([k, v]) => (
                <li key={k} className="flex justify-between">
                  <span className="text-muted-foreground">{k}</span>
                  <span className="tabular font-semibold">{v}</span>
                </li>
              ))}
            </ul>
            <div className="mt-3 rounded-lg bg-turmeric/15 px-2.5 py-2 text-[12px] leading-snug text-amber-800 dark:text-amber-200">
              Iron below target
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (id === "camera") {
    return (
      <div className="relative w-full max-w-md">
        <div className="aspect-video w-full rounded-xl bg-[#DDE3DF] p-3">
          <div className="grid h-full grid-cols-3 grid-rows-2 gap-2">
            <div className="row-span-2 rounded-lg bg-[#F4EFE2]" />
            <div className="rounded-lg bg-[#E0A21F]" />
            <div className="rounded-lg bg-[#E8C35A]" />
            <div className="rounded-lg bg-[#D9A866]" />
            <div className="rounded-lg bg-[#FBFAF5]" />
          </div>
        </div>
        {[
          { top: "6%", left: "3%", w: "32%", h: "88%", label: "Rice 96%" },
          { top: "6%", left: "36%", w: "30%", h: "42%", label: "Dal 93%" },
          { top: "52%", left: "68%", w: "29%", h: "42%", label: "Curd 91%" },
        ].map((box, i) => (
          <motion.div
            key={box.label}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.25 + i * 0.2 }}
            style={{ top: box.top, left: box.left, width: box.w, height: box.h }}
            className="absolute rounded-lg border-2 border-primary"
          >
            <span className="absolute left-1.5 top-1.5 rounded-full bg-sidebar px-2 py-0.5 text-[11px] font-semibold text-[#F5F7F2]">
              {box.label}
            </span>
          </motion.div>
        ))}
      </div>
    );
  }

  if (id === "nutrition") {
    return (
      <div className="w-full max-w-md space-y-3">
        {[
          { label: "Energy", value: "642 kcal", pct: 92 },
          { label: "Protein", value: "19 g", pct: 76 },
          { label: "Iron", value: "3.1 mg", pct: 41, low: true },
          { label: "Calcium", value: "212 mg", pct: 62 },
          { label: "Fibre", value: "7.4 g", pct: 58 },
        ].map((n) => (
          <div key={n.label} className="grid grid-cols-[5.5rem_1fr_4.5rem] items-center gap-3 text-sm">
            <span className="text-muted-foreground">{n.label}</span>
            <div className="h-2 rounded-full bg-secondary">
              <div className={cn("h-full rounded-full", n.low ? "bg-turmeric" : "bg-primary")} style={{ width: `${n.pct}%` }} />
            </div>
            <span className="tabular text-right font-semibold">{n.value}</span>
          </div>
        ))}
        <p className="pt-2 text-xs text-muted-foreground">Bars show share of the per-meal target (ICMR-NIN 2020).</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-xl">
      <div className="flex items-end justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Meals meeting targets, this week</p>
          <p className="font-display tabular mt-1 text-4xl font-extrabold">79.6%</p>
        </div>
        <p className="text-sm text-muted-foreground">2,614 trays</p>
      </div>
      <div className="mt-6 flex h-40 items-end gap-3">
        {week.map((w) => (
          <div key={w.d} className="flex flex-1 flex-col items-center gap-2">
            <div
              className={cn("w-full rounded-t-lg", w.v < 70 ? "bg-turmeric" : "bg-primary")}
              style={{ height: `${w.v * 1.4}px` }}
              title={`${w.d}: ${w.v}%`}
            />
            <span className="text-xs text-muted-foreground">{w.d}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
