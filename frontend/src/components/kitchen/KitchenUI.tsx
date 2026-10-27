import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export function PageIntro({ title, description, actions }: { title: string; description: string; actions?: ReactNode }) {
  return (
    <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div className="max-w-2xl">
        <h1 className="font-display text-3xl font-bold tracking-[-0.03em] md:text-[2.4rem]">{title}</h1>
        <p className="mt-2 leading-relaxed text-muted-foreground">{description}</p>
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

/** Collapsible plain-English explainer shown on every kitchen page. */
export function HowItWorks({ steps, children }: { steps: string[]; children?: ReactNode }) {
  return (
    <details className="group rounded-2xl border border-border bg-card">
      <summary className="flex cursor-pointer list-none items-center justify-between px-5 py-4 font-medium [&::-webkit-details-marker]:hidden">
        How this works
        <ChevronDown size={18} className="text-muted-foreground transition-transform group-open:rotate-180" />
      </summary>
      <div className="border-t border-border px-5 pb-5 pt-4">
        <ol className="list-decimal space-y-2 pl-5 text-sm leading-relaxed text-muted-foreground marker:text-primary">
          {steps.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ol>
        {children}
      </div>
    </details>
  );
}

export function Panel({ title, description, children, className, action }: {
  title?: string;
  description?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}) {
  return (
    <section className={cn("min-w-0 rounded-2xl border border-border bg-card p-5 md:p-6", className)}>
      {(title || action) && (
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            {title && <h2 className="font-display text-lg font-bold tracking-[-0.02em]">{title}</h2>}
            {description && <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function Stat({ label, value, sub, tone = "default" }: {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  tone?: "default" | "warn" | "good";
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p
        className={cn(
          "font-display tabular mt-1.5 text-[1.9rem] font-extrabold leading-none tracking-[-0.02em]",
          tone === "warn" && "text-amber-700 dark:text-amber-400",
          tone === "good" && "text-primary"
        )}
      >
        {value}
      </p>
      {sub && <p className="mt-2 text-sm text-muted-foreground">{sub}</p>}
    </div>
  );
}

export function SampleBanner({ onClear, clearing }: { onClear: () => void; clearing?: boolean }) {
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-turmeric/40 bg-turmeric/10 px-5 py-3.5 text-sm sm:flex-row sm:items-center sm:justify-between">
      <p className="text-amber-900 dark:text-amber-200">
        You're looking at eight weeks of generated sample data. Log your own services to replace it.
      </p>
      <button
        onClick={onClear}
        disabled={clearing}
        className="self-start rounded-lg border border-turmeric/50 px-3 py-1.5 font-medium text-amber-900 hover:bg-turmeric/15 disabled:opacity-50 dark:text-amber-200 sm:self-auto"
      >
        {clearing ? "Clearing…" : "Clear sample data"}
      </button>
    </div>
  );
}

export function Bar({ pct, tone = "primary" }: { pct: number; tone?: "primary" | "warn" | "muted" }) {
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
      <div
        className={cn(
          "h-full rounded-full",
          tone === "primary" && "bg-primary",
          tone === "warn" && "bg-turmeric",
          tone === "muted" && "bg-steel"
        )}
        style={{ width: `${Math.max(0, Math.min(100, pct))}%` }}
      />
    </div>
  );
}

export const fieldClass =
  "h-11 w-full rounded-xl border border-border bg-background px-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20";
