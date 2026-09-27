import { cn } from "@/lib/utils";

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-secondary/70", className)}
      {...props}
    />
  );
}

export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-xl border border-border bg-card p-6", className)}>
      <Skeleton className="h-4 w-24" />
      <Skeleton className="mt-3 h-7 w-16" />
    </div>
  );
}

export function TableRowSkeleton({ columns = 4 }: { columns?: number }) {
  return (
    <div className="flex items-center gap-4 border-b border-border py-3 last:border-0">
      {Array.from({ length: columns }).map((_, i) => (
        <Skeleton key={i} className={cn("h-4", i === 0 ? "w-1/3" : "flex-1")} />
      ))}
    </div>
  );
}

export function ChartSkeleton({ height = 224 }: { height?: number }) {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="mt-1.5 h-3 w-48" />
      <Skeleton className="mt-5 w-full" style={{ height }} />
    </div>
  );
}
