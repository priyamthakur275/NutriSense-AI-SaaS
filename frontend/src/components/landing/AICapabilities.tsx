import { motion } from "framer-motion";
import { Bot, Eye, ShieldCheck, LineChart, Sparkles, MessageSquareText, Building2 } from "lucide-react";
import { SectionHeading } from "@/components/landing/SectionHeading";

const capabilities = [
  {
    icon: Bot,
    title: "Multi-Agent Orchestration",
    description:
      "Orchestrator, Suggestion, and Planner agents collaborate over LangGraph — each specialized, all grounded in structured data.",
  },
  {
    icon: Eye,
    title: "Vision AI",
    description:
      "Fine-tuned detection and segmentation models recognize multi-item plates, even on crowded institutional trays.",
  },
  {
    icon: ShieldCheck,
    title: "Compliance Engine",
    description:
      "Rule-based reasoning maps nutrient outputs to WHO, FSSAI, and ICMR-NIN thresholds with zero hallucination risk.",
  },
  {
    icon: LineChart,
    title: "Predictive Analytics",
    description:
      "Rolling deficit patterns feed forecasting models that flag at-risk nutrition trends before they compound.",
  },
  {
    icon: Sparkles,
    title: "Prediction & Forecasting",
    description:
      "Next-day and next-week nutrient shortfalls are predicted from historical meal and attendance data.",
  },
  {
    icon: MessageSquareText,
    title: "Recommendation Agent",
    description:
      "Corrective menu suggestions are generated from compliance reports — transparent, sourced, and auditable.",
  },
  {
    icon: Building2,
    title: "Institution Intelligence",
    description:
      "Cross-institution benchmarking surfaces best practices and systemic nutrition gaps at scale.",
  },
];

export function AICapabilities() {
  return (
    <section id="ai-capabilities" className="relative overflow-hidden px-6 py-24">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_50%_50%_at_50%_50%,hsl(var(--primary)/0.08),transparent)]" />

      <div className="mx-auto max-w-7xl">
        <SectionHeading
          eyebrow="Artificial Intelligence"
          title="A full agentic AI stack"
          description="Not just recognition — a coordinated system of specialized agents that reason, plan, and recommend."
        />

        <div className="mt-16 grid grid-cols-1 gap-px overflow-hidden rounded-2xl border border-border bg-border md:grid-cols-2 lg:grid-cols-3">
          {capabilities.map((cap, i) => (
            <motion.div
              key={cap.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.4, delay: (i % 3) * 0.08 }}
              className="group relative bg-card p-7"
            >
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-gradient-to-br from-primary/20 to-primary/5 text-primary">
                <cap.icon size={20} />
              </div>
              <h3 className="text-base font-semibold">{cap.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {cap.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
