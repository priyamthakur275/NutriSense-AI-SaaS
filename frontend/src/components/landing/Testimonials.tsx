import { motion } from "framer-motion";
import { Quote } from "lucide-react";
import { SectionHeading } from "@/components/landing/SectionHeading";
import { Card } from "@/components/ui/Card";

const testimonials = [
  {
    quote:
      "We went from spot-checking a handful of trays a week to full daily coverage. The compliance dashboard is the first thing our nutritionist opens every morning.",
    name: "Dr. Ananya Rao",
    role: "Chief Nutritionist",
    org: "Apollo Institutional Health",
  },
  {
    quote:
      "Attendance and meal records used to live in two different systems. NutriSense finally connects them — our audits take a fraction of the time now.",
    name: "Rajesh Menon",
    role: "Hostel Administrator",
    org: "NIT Trichy",
  },
  {
    quote:
      "As a student, I actually check my own nutrition summary now. Seeing the breakdown made me think differently about what I pick at the counter.",
    name: "Sneha Iyer",
    role: "Student",
    org: "BMS College of Engineering",
  },
  {
    quote:
      "The recommendation agent flagged a recurring iron deficit two weeks before we would have caught it manually. That's the whole value proposition, right there.",
    name: "Farhan Sheikh",
    role: "Canteen Operations Lead",
    org: "Tata Institutional Canteens",
  },
];

export function Testimonials() {
  return (
    <section className="px-6 py-24">
      <div className="mx-auto max-w-7xl">
        <SectionHeading
          eyebrow="Testimonials"
          title="Trusted by nutrition teams and students alike"
          description="From canteen staff to hostel administrators — real feedback from institutions running NutriSense AI."
        />

        <div className="mt-16 grid grid-cols-1 gap-5 md:grid-cols-2">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.4, delay: (i % 2) * 0.1 }}
            >
              <Card className="relative h-full p-7">
                <Quote className="absolute right-6 top-6 text-primary/10" size={40} />
                <p className="relative text-sm leading-relaxed text-foreground/90">
                  "{t.quote}"
                </p>
                <div className="mt-6 flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                    {t.name.split(" ").map((n) => n[0]).join("")}
                  </span>
                  <div>
                    <p className="text-sm font-semibold">{t.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {t.role} · {t.org}
                    </p>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
