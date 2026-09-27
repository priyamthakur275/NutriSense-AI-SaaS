import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus } from "lucide-react";
import { SectionHeading } from "@/components/landing/SectionHeading";
import { cn } from "@/lib/utils";

const faqs = [
  {
    question: "What kind of institutions is NutriSense AI built for?",
    answer:
      "Schools, colleges, hospitals, hostels, corporate canteens, and government meal schemes — anywhere food is served through a systematic, repeatable process rather than an à la carte menu.",
  },
  {
    question: "How accurate is the food recognition?",
    answer:
      "Our vision pipeline targets 80%+ top-1 accuracy on validation data, and improves further with institution-specific fine-tuning as more tray images are captured.",
  },
  {
    question: "Which dietary standards does the compliance engine use?",
    answer:
      "Meals are checked against WHO nutrition guidance, FSSAI's Eat Right India standards, and ICMR-NIN recommended dietary allowances for Indian populations.",
  },
  {
    question: "Can we deploy on our own infrastructure?",
    answer:
      "Yes. The platform is fully containerized with Docker Compose, so it can run on-premise, on a private cloud, or on any managed Kubernetes environment.",
  },
  {
    question: "How is student and attendance data protected?",
    answer:
      "All data is encrypted in transit and at rest, access is enforced through role-based permissions, and every action is captured in an auditable log.",
  },
  {
    question: "Do you offer a free tier to evaluate the platform?",
    answer:
      "Yes — you can register and explore the dashboard immediately. Reach out for a guided pilot with your institution's own meal data.",
  },
];

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section id="faq" className="px-6 py-24">
      <div className="mx-auto max-w-3xl">
        <SectionHeading
          eyebrow="FAQ"
          title="Frequently asked questions"
          description="Everything you need to know before rolling out NutriSense AI."
        />

        <div className="mt-12 flex flex-col gap-3">
          {faqs.map((faq, i) => {
            const isOpen = openIndex === i;
            return (
              <motion.div
                key={faq.question}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.35, delay: i * 0.04 }}
                className="overflow-hidden rounded-xl border border-border bg-card"
              >
                <button
                  onClick={() => setOpenIndex(isOpen ? null : i)}
                  className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
                  aria-expanded={isOpen}
                >
                  <span className="text-sm font-medium">{faq.question}</span>
                  <motion.span
                    animate={{ rotate: isOpen ? 45 : 0 }}
                    transition={{ duration: 0.25 }}
                    className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-secondary text-muted-foreground"
                  >
                    <Plus size={14} />
                  </motion.span>
                </button>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                      className={cn("overflow-hidden")}
                    >
                      <p className="px-5 pb-4 text-sm leading-relaxed text-muted-foreground">
                        {faq.answer}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
