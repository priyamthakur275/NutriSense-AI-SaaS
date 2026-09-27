import { useRef } from "react";
import { motion, useMotionTemplate, useMotionValue } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Sparkles, Camera, ShieldCheck, TrendingUp, Play } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { AnimatedCounter } from "@/components/landing/AnimatedCounter";

const floatingCards = [
  {
    icon: Camera,
    title: "Tray Scanned",
    subtitle: "6 items detected",
    className: "left-[-4%] top-[14%] md:left-[-8%]",
    delay: 0.5,
  },
  {
    icon: ShieldCheck,
    title: "Compliance",
    subtitle: "94% · WHO / FSSAI",
    className: "right-[-4%] top-[6%] md:right-[-9%]",
    delay: 0.7,
  },
  {
    icon: TrendingUp,
    title: "Protein intake",
    subtitle: "+12% this week",
    className: "right-[2%] bottom-[8%] md:right-[-4%]",
    delay: 0.9,
  },
];

const institutions = ["BMSCE", "Apollo Hospitals", "NIT Trichy", "Tata Canteens", "Akshaya Patra"];

export function Hero() {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    mouseX.set(e.clientX - rect.left);
    mouseY.set(e.clientY - rect.top);
  }

  const spotlight = useMotionTemplate`radial-gradient(600px circle at ${mouseX}px ${mouseY}px, hsl(var(--primary) / 0.10), transparent 80%)`;

  return (
    <section
      ref={containerRef}
      onMouseMove={handleMouseMove}
      className="relative overflow-hidden px-6 pb-20 pt-24 md:pb-28 md:pt-32"
    >
      {/* Background layers */}
      <div className="pointer-events-none absolute inset-0 -z-20 bg-grid [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,black,transparent)] opacity-[0.35]" />
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_60%_50%_at_50%_-10%,hsl(var(--primary)/0.18),transparent)]" />
      <motion.div
        className="pointer-events-none absolute inset-0 -z-10"
        style={{ backgroundImage: spotlight }}
      />

      <div className="mx-auto flex max-w-4xl flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-6 flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-4 py-1.5 text-xs font-medium text-muted-foreground glow"
        >
          <Sparkles size={14} className="text-primary" />
          Agentic AI for institutional nutrition
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.05 }}
          className="text-4xl font-bold tracking-tight md:text-6xl lg:text-7xl"
        >
          Nutrition monitoring, <br className="hidden md:block" />
          <span className="text-gradient">automated end-to-end.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground"
        >
          NutriSense AI turns meal-tray images into compliance-scored
          nutrition data — with attendance tracking, dietary-standard
          checks, and multi-agent recommendations, all in one dashboard.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.22 }}
          className="mt-10 flex flex-col gap-3 sm:flex-row"
        >
          <Button size="lg" onClick={() => navigate("/register")} className="shadow-lg shadow-primary/20">
            Start free <ArrowRight size={16} />
          </Button>
          <Button size="lg" variant="outline">
            <Play size={16} /> Watch demo
          </Button>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-16 grid grid-cols-3 gap-8 border-y border-border/60 py-6 sm:gap-16"
        >
          {[
            { value: 2, suffix: "M+", label: "Meals analyzed" },
            { value: 99.5, suffix: "%", label: "Uptime SLA", decimals: 1 },
            { value: 40, suffix: "+", label: "Institutions" },
          ].map((stat) => (
            <div key={stat.label} className="flex flex-col items-center">
              <AnimatedCounter
                value={stat.value}
                suffix={stat.suffix}
                decimals={stat.decimals ?? 0}
                className="text-2xl font-bold tabular-nums md:text-3xl"
              />
              <span className="mt-1 text-xs text-muted-foreground md:text-sm">
                {stat.label}
              </span>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Product mockup with floating cards */}
      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.8, delay: 0.35 }}
        className="relative mx-auto mt-20 max-w-5xl"
      >
        <div className="pointer-events-none absolute -inset-x-10 -inset-y-10 -z-10 bg-[radial-gradient(ellipse_50%_50%_at_50%_50%,hsl(var(--primary)/0.15),transparent)] blur-2xl" />

        <div className="glow overflow-hidden rounded-2xl border border-border bg-card">
          <div className="flex items-center gap-1.5 border-b border-border bg-secondary/40 px-4 py-3">
            <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
            <span className="h-2.5 w-2.5 rounded-full bg-yellow-400" />
            <span className="h-2.5 w-2.5 rounded-full bg-green-400" />
            <span className="ml-4 rounded-md bg-background px-3 py-1 text-xs text-muted-foreground">
              app.nutrisense.ai/dashboard
            </span>
          </div>
          <div className="grid grid-cols-1 gap-px bg-border md:grid-cols-3">
            <div className="col-span-1 space-y-3 bg-card p-6 md:col-span-2">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold">Today's compliance</p>
                <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                  Live
                </span>
              </div>
              <div className="flex h-40 items-end gap-2">
                {[52, 68, 44, 80, 63, 91, 74].map((h, i) => (
                  <motion.div
                    key={i}
                    initial={{ height: 0 }}
                    whileInView={{ height: `${h}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: i * 0.06, ease: "easeOut" }}
                    className="flex-1 rounded-t-md bg-gradient-to-t from-primary/80 to-primary/30"
                  />
                ))}
              </div>
            </div>
            <div className="col-span-1 space-y-4 bg-card p-6">
              {[
                { label: "Protein", value: 82 },
                { label: "Iron", value: 61 },
                { label: "Calcium", value: 74 },
              ].map((n) => (
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
                      transition={{ duration: 0.8, ease: "easeOut" }}
                      className="h-full rounded-full bg-primary"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {floatingCards.map((card) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.6, delay: card.delay }}
            whileHover={{ y: -4 }}
            className={`glass absolute hidden w-48 rounded-xl p-3 shadow-xl md:flex ${card.className}`}
          >
            <div className="flex items-center gap-3">
              <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <card.icon size={16} />
              </span>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold">{card.title}</p>
                <p className="truncate text-xs text-muted-foreground">{card.subtitle}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Trusted by */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="mx-auto mt-24 flex max-w-4xl flex-col items-center gap-6"
      >
        <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          Trusted by institutions across India
        </p>
        <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-4 opacity-70 grayscale">
          {institutions.map((name) => (
            <span key={name} className="text-sm font-semibold md:text-base">
              {name}
            </span>
          ))}
        </div>
      </motion.div>
    </section>
  );
}
