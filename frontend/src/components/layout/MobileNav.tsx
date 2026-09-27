import { useState } from "react";
import { NavLink } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import {
  Bell,
  X,
  Camera,
  LogOut,
  Settings,
  Users,
  Bot,
  FileBarChart,
  ShieldCheck,
  User,
  LayoutDashboard,
  Leaf,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/store/uiStore";
import { LogoutConfirmModal } from "@/components/layout/LogoutConfirmModal";

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

export function MobileNav() {
  const { mobileNavOpen, setMobileNavOpen } = useUIStore();
  const [logoutOpen, setLogoutOpen] = useState(false);

  return (
    <>
      <AnimatePresence>
        {mobileNavOpen && (
          <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setMobileNavOpen(false)}
            className="fixed inset-0 z-[90] bg-black/40 backdrop-blur-sm md:hidden"
          />
          <motion.div
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "tween", duration: 0.25 }}
            className="fixed inset-y-0 left-0 z-[95] flex w-72 flex-col bg-card shadow-2xl md:hidden"
          >
            <div className="flex h-16 items-center justify-between border-b border-border px-5">
              <div className="flex items-center gap-2 font-semibold">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <Leaf size={18} />
                </span>
                NutriSense AI
              </div>
              <button
                onClick={() => setMobileNavOpen(false)}
                aria-label="Close menu"
                className="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-secondary"
              >
                <X size={16} />
              </button>
            </div>

            <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-3">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  onClick={() => setMobileNavOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                    )
                  }
                >
                  <item.icon size={18} />
                  {item.label}
                </NavLink>
              ))}
            </nav>

            <div className="border-t border-border p-3">
              <button
                onClick={() => {
                  setMobileNavOpen(false);
                  setLogoutOpen(true);
                }}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-red-500 transition-colors hover:bg-red-500/10"
              >
                <LogOut size={18} /> Log out
              </button>
            </div>
          </motion.div>
        </>
      )}
      </AnimatePresence>
      <LogoutConfirmModal open={logoutOpen} onOpenChange={setLogoutOpen} />
    </>
  );
}
