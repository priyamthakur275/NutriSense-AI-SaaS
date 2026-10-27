import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Leaf,
  User,
  ShieldCheck,
  Bell,
  ChevronsLeft,
  Settings,
  FileBarChart,
  Bot,
  LayoutDashboard,
  Users,
  ChevronsRight,
  Camera,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/store/uiStore";
import { Tooltip, TooltipProvider } from "@/components/ui/Tooltip";

const navItems = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutDashboard, end: true },
  { label: "Students", to: "/dashboard/students", icon: Users },
  { label: "Meals", to: "/dashboard/meals", icon: Camera },
  { label: "Nutrition", to: "/dashboard/nutrition", icon: Leaf },
  { label: "AI Insights", to: "/dashboard/ai-insights", icon: Bot },
  { label: "Compliance", to: "/dashboard/compliance", icon: ShieldCheck },
  { label: "Reports", to: "/dashboard/reports", icon: FileBarChart },
  { label: "Notifications", to: "/dashboard/notifications", icon: Bell },
  { label: "Settings", to: "/dashboard/settings", icon: Settings },
  { label: "Profile", to: "/dashboard/profile", icon: User },
];

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore();

  return (
    <TooltipProvider>
      <motion.aside
        animate={{ width: sidebarCollapsed ? 76 : 256 }}
        transition={{ duration: 0.25, ease: "easeInOut" }}
        className="relative hidden flex-shrink-0 flex-col bg-sidebar text-sidebar-foreground md:flex"
      >
        <div className="flex h-16 items-center gap-2.5 overflow-hidden border-b border-white/[0.07] px-5 font-semibold text-[#F5F7F2]">
          <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-[#E3A21A] text-[#12261D]">
            <Leaf size={18} />
          </span>
          {!sidebarCollapsed && <span className="whitespace-nowrap">NutriSense AI</span>}
        </div>

        <nav className="flex flex-1 flex-col gap-1 p-3">
          {navItems.map((item) => {
            const link = (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    sidebarCollapsed && "justify-center px-0",
                    isActive
                      ? "bg-sidebar-active text-[#F5F7F2] shadow-[inset_3px_0_0_#E3A21A]"
                      : "text-sidebar-muted hover:bg-white/[0.05] hover:text-sidebar-foreground"
                  )
                }
              >
                <item.icon size={18} className="flex-shrink-0" />
                {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
              </NavLink>
            );

            return sidebarCollapsed ? (
              <Tooltip key={item.to} content={item.label} side="right">
                {link}
              </Tooltip>
            ) : (
              link
            );
          })}
        </nav>

        <button
          onClick={toggleSidebar}
          aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="flex h-12 items-center justify-center gap-2 border-t border-white/[0.07] text-sm text-sidebar-muted transition-colors hover:bg-white/[0.05] hover:text-sidebar-foreground"
        >
          {sidebarCollapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
          {!sidebarCollapsed && "Collapse"}
        </button>
      </motion.aside>
    </TooltipProvider>
  );
}
