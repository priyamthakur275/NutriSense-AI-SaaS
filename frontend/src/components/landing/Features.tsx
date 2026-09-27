import { motion } from "framer-motion";
import {
  Camera,
  ShieldCheck,
  Users,
  Bot,
  LineChart,
  Bell,
  Scale,
  Database,
  Workflow,
  Fingerprint,
  FileBarChart,
  Zap,
} from "lucide-react";
import { SectionHeading } from "@/components/landing/SectionHeading";
import { Card } from "@/components/ui/Card";

const features = [
  {
    icon: Camera,
    title: "Food Recognition",
    description: "Computer-vision models identify food items directly from tray images in real time.",
  },
  {
    icon: Scale,
    title: "Portion Estimation",
    description: "Depth-aware algorithms convert bounding boxes into accurate serving weights.",
  },
  {
    icon: Database,
    title: "Nutrition Lookup",
    description: "Every item is mapped to USDA and ICMR-NIN nutrient databases automatically.",
  },
  {
    icon: ShieldCheck,
    title: "Compliance Engine",
    description: "Meals are scored against WHO, FSSAI, and ICMR dietary standards instantly.",
  },
  {
    icon: Bot,
    title: "Agentic Recommendations",
    description: "LangGraph-orchestrated agents turn compliance gaps into corrective menu suggestions.",
  },
  {
    icon: Workflow,
    title: "Menu Planning",
    description: "A planner agent proposes next-day menus from rolling nutrient-deficit trends.",
  },
  {
    icon: Users,
    title: "Attendance Tracking",
    description: "Meal distribution is linked to verified, face-recognition-backed attendance.",
  },
  {
    icon: Fingerprint,
    title: "Role-Based Access",
    description: "Granular permissions for students, staff, admins, and super admins.",
  },
  {
    icon: LineChart,
    title: "Analytics Dashboard",
    description: "Trend analysis, nutrient breakdowns, and institutional performance in one view.",
  },
  {
    icon: FileBarChart,
    title: "Compliance Reports",
    description: "Exportable PDF reports for audits, funding bodies, and internal reviews.",
  },
  {
    icon: Bell,
    title: "Real-time Alerts",
    description: "Canteen managers are notified the moment repeated compliance failures occur.",
  },
  {
    icon: Zap,
    title: "Sub-5s Analysis",
    description: "Full tray-to-compliance pipeline completes in under five seconds, at scale.",
  },
];

export function Features() {
  return (
    <section id="features" className="px-6 py-24">
      <div className="mx-auto max-w-7xl">
        <SectionHeading
          eyebrow="Platform"
          title="Everything institutions need"
          description="A single platform that unifies recognition, compliance, attendance, and decision-making."
        />

        <div className="mt-16 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.4, delay: (i % 6) * 0.05 }}
              whileHover={{ y: -4 }}
              className="group"
            >
              <Card className="relative h-full overflow-hidden p-6 transition-shadow duration-300 hover:shadow-lg hover:shadow-primary/5">
                <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-primary/5 opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-100" />
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-accent text-accent-foreground transition-transform duration-300 group-hover:scale-110">
                  <feature.icon size={20} />
                </div>
                <h3 className="text-base font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
