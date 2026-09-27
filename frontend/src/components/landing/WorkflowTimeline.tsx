import { motion } from "framer-motion";
import { Camera, ScanEye, FlaskConical, Bot, ShieldCheck, FileText } from "lucide-react";
import { SectionHeading } from "@/components/landing/SectionHeading";

const steps = [
  { icon: Camera, title: "Capture", description: "Tray and attendance cameras capture images at the distribution point." },
  { icon: ScanEye, title: "Recognize", description: "Vision models identify each food item and estimate portion size." },
  { icon: FlaskConical, title: "Analyse", description: "Nutrient profiles are aggregated from verified nutrition databases." },
  { icon: ShieldCheck, title: "Compliance", description: "The meal is scored against WHO, FSSAI, and ICMR thresholds." },
  { icon: Bot, title: "Recommend", description: "Agents generate corrective, menu-level recommendations." },
  { icon: FileText, title: "Report", description: "Dashboards and exportable reports close the loop for admins." },
];

export function WorkflowTimeline() {
  return (
    <section id="workflow" className="px-6 py-24">
      <div className="mx-auto max-w-7xl">
        <SectionHeading
          eyebrow="How it works"
          title="From tray to insight in six steps"
          description="A single, automated pipeline — no manual bottlenecks."
        />

        <div className="relative mt-20">
          {/* Connector line */}
          <div className="absolute left-6 top-0 h-full w-px bg-border md:left-1/2 md:h-px md:w-full md:top-6" />
          <motion.div
            initial={{ scaleY: 0, scaleX: 0 }}
            whileInView={{ scaleY: 1, scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
            style={{ transformOrigin: "top left" }}
            className="absolute left-6 top-0 h-full w-px origin-top bg-primary md:left-0 md:h-px md:w-full md:top-6 md:origin-left"
          />

          <div className="grid grid-cols-1 gap-10 md:grid-cols-6 md:gap-4">
            {steps.map((step, i) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: i * 0.12 }}
                className="relative flex gap-4 pl-16 md:flex-col md:items-center md:gap-0 md:pl-0 md:text-center"
              >
                <span className="absolute left-0 flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full border-2 border-primary bg-background text-primary shadow-sm md:relative md:mb-4">
                  <step.icon size={20} />
                  <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                    {i + 1}
                  </span>
                </span>
                <div>
                  <h3 className="font-semibold">{step.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground md:px-2">{step.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
