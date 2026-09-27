import { motion } from "framer-motion";
import { KeyRound, Lock, Fingerprint, ScrollText, ServerCog } from "lucide-react";
import { SectionHeading } from "@/components/landing/SectionHeading";

const items = [
  {
    icon: KeyRound,
    title: "JWT Authentication",
    description: "Short-lived, signed access tokens with automatic session invalidation.",
  },
  {
    icon: Lock,
    title: "Encryption at Rest & Transit",
    description: "All meal, attendance, and user data is encrypted end-to-end.",
  },
  {
    icon: Fingerprint,
    title: "Role-Based Access Control",
    description: "Granular permissions across student, staff, admin, and super-admin roles.",
  },
  {
    icon: ScrollText,
    title: "Audit Logs",
    description: "Every compliance decision and data access is traceable and timestamped.",
  },
  {
    icon: ServerCog,
    title: "Secure Storage",
    description: "Containerized, isolated infrastructure with automated health checks.",
  },
];

export function Security() {
  return (
    <section id="security" className="px-6 py-24">
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-2 lg:items-center">
          <SectionHeading
            align="left"
            eyebrow="Security"
            title="Institution-grade security, by default"
            description="Handling nutrition and attendance data for thousands of students demands more than best-effort security. NutriSense AI is built with encryption, RBAC, and full auditability from day one."
          />

          <div className="flex flex-col gap-4">
            {items.map((item, i) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                className="flex items-start gap-4 rounded-xl border border-border bg-card p-4"
              >
                <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                  <item.icon size={18} />
                </span>
                <div>
                  <h3 className="text-sm font-semibold">{item.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
