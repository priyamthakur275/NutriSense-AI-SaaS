import { cn } from "@/lib/utils";

interface SectionHeadingProps {
  /** Kept for API compatibility; no longer rendered (headings stand on their own). */
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "center" | "left";
  className?: string;
}

export function SectionHeading({ title, description, align = "center", className }: SectionHeadingProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-4",
        align === "center" ? "mx-auto max-w-2xl items-center text-center" : "max-w-2xl",
        className
      )}
    >
      <h2 className="font-display text-[2rem] font-bold leading-[1.05] tracking-[-0.03em] md:text-[2.75rem]">
        {title}
      </h2>
      {description && (
        <p className="max-w-[38rem] text-base leading-relaxed text-muted-foreground md:text-lg">{description}</p>
      )}
    </div>
  );
}
