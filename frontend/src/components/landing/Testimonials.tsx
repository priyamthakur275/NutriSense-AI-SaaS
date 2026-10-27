import { SectionHeading } from "@/components/landing/SectionHeading";

/* Who uses NutriSense and what each role does with it. (Replaces a section of
   invented customer quotes: a project shouldn't attribute words to real
   people or institutions.) */
const roles = [
  {
    role: "Canteen manager",
    does: "Scans trays during service and sees which dishes fall short before the next menu is printed.",
    sees: "Per-meal compliance, portion drift, waste",
  },
  {
    role: "Nutritionist",
    does: "Reviews weekly nutrient gaps and approves the planner agent's suggested menu changes.",
    sees: "Micronutrient trends against ICMR-NIN targets",
  },
  {
    role: "Hostel or school admin",
    does: "Downloads audit-ready reports and tracks attendance against meals served.",
    sees: "Attendance, reports, institution settings",
  },
  {
    role: "Student",
    does: "Checks what their own plate contained and how it compares with the daily requirement.",
    sees: "A personal nutrition summary",
  },
];

export function Testimonials() {
  return (
    <section className="px-5 py-24 md:px-8">
      <div className="mx-auto max-w-7xl">
        <SectionHeading
          align="left"
          title="One tray, four people who need the answer"
          description="Every role sees the same scan, framed for the decision they make."
        />
        <div className="mt-14 grid gap-px overflow-hidden rounded-[22px] border border-border bg-border md:grid-cols-2">
          {roles.map((r) => (
            <article key={r.role} className="flex flex-col gap-3 bg-card p-7 md:p-9">
              <h3 className="font-display text-xl font-bold">{r.role}</h3>
              <p className="max-w-[30rem] leading-relaxed text-muted-foreground">{r.does}</p>
              <p className="mt-auto pt-3 text-sm font-medium text-primary">{r.sees}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
