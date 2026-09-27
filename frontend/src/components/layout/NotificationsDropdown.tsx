import { Bell, ShieldAlert, TrendingDown, CheckCircle2 } from "lucide-react";
import {
  Dropdown,
  DropdownTrigger,
  DropdownContent,
  DropdownItem,
  DropdownLabel,
  DropdownSeparator,
} from "@/components/ui/Dropdown";
import { Badge } from "@/components/ui/Badge";

const notifications = [
  {
    icon: ShieldAlert,
    tone: "warning" as const,
    title: "Compliance dip detected",
    description: "Hostel Block C fell below 80% for the third day.",
    time: "12m ago",
  },
  {
    icon: TrendingDown,
    tone: "destructive" as const,
    title: "Iron intake deficit",
    description: "Rolling 7-day average is 18% under threshold.",
    time: "1h ago",
  },
  {
    icon: CheckCircle2,
    tone: "success" as const,
    title: "Weekly report ready",
    description: "Your compliance report for this week has been generated.",
    time: "3h ago",
  },
];

const toneClass: Record<string, string> = {
  warning: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
  destructive: "bg-red-500/10 text-red-600 dark:text-red-400",
  success: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
};

export function NotificationsDropdown() {
  return (
    <Dropdown>
      <DropdownTrigger asChild>
        <button
          aria-label="Notifications"
          className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-border transition-colors hover:bg-secondary"
        >
          <Bell size={16} />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-background" />
        </button>
      </DropdownTrigger>
      <DropdownContent align="end" className="w-80">
        <div className="flex items-center justify-between px-2.5 py-1.5">
          <DropdownLabel className="p-0">Notifications</DropdownLabel>
          <Badge variant="secondary">{notifications.length} new</Badge>
        </div>
        <DropdownSeparator />
        {notifications.map((n) => (
          <DropdownItem key={n.title} className="items-start gap-3 py-2.5">
            <span className={`mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg ${toneClass[n.tone]}`}>
              <n.icon size={15} />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{n.title}</p>
              <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
                {n.description}
              </p>
              <p className="mt-1 text-[11px] text-muted-foreground">{n.time}</p>
            </div>
          </DropdownItem>
        ))}
        <DropdownSeparator />
        <DropdownItem className="justify-center text-xs font-medium text-primary">
          View all notifications
        </DropdownItem>
      </DropdownContent>
    </Dropdown>
  );
}
