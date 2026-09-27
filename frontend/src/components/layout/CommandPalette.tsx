import { useEffect } from "react";
import { Command } from "cmdk";
import { useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Camera,
  ShieldCheck,
  Users,
  Bot,
  FileBarChart,
  Settings,
  Moon,
  Sun,
  LogOut,
  Search,
} from "lucide-react";
import { useUIStore } from "@/store/uiStore";
import { useThemeStore } from "@/store/themeStore";
import { useAuthStore } from "@/store/authStore";

const navCommands = [
  { label: "Overview", to: "/dashboard", icon: LayoutDashboard },
  { label: "Meals", to: "/dashboard/meals", icon: Camera },
  { label: "Compliance", to: "/dashboard/compliance", icon: ShieldCheck },
  { label: "Attendance", to: "/dashboard/attendance", icon: Users },
  { label: "Recommendations", to: "/dashboard/recommendations", icon: Bot },
  { label: "Reports", to: "/dashboard/reports", icon: FileBarChart },
  { label: "Settings", to: "/dashboard/settings", icon: Settings },
];

export function CommandPalette() {
  const { commandPaletteOpen, setCommandPaletteOpen } = useUIStore();
  const { theme, toggleTheme } = useThemeStore();
  const { logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
      if (e.key === "Escape") {
        setCommandPaletteOpen(false);
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [commandPaletteOpen, setCommandPaletteOpen]);

  function runCommand(action: () => void) {
    setCommandPaletteOpen(false);
    action();
  }

  if (!commandPaletteOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center bg-black/40 px-4 pt-[15vh] backdrop-blur-sm"
      onClick={() => setCommandPaletteOpen(false)}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg overflow-hidden rounded-2xl border border-border bg-card shadow-2xl"
      >
        <Command label="Command palette" className="flex flex-col">
          <div className="flex items-center gap-3 border-b border-border px-4">
            <Search size={16} className="text-muted-foreground" />
            <Command.Input
              autoFocus
              placeholder="Search pages, actions..."
              className="h-12 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
            <kbd className="hidden rounded border border-border px-1.5 py-0.5 text-[10px] text-muted-foreground sm:inline">
              Esc
            </kbd>
          </div>

          <Command.List className="max-h-80 overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </Command.Empty>

            <Command.Group heading="Navigate" className="px-2 py-1.5 text-xs font-semibold text-muted-foreground [&_[cmdk-group-items]]:mt-1">
              {navCommands.map((item) => (
                <Command.Item
                  key={item.to}
                  onSelect={() => runCommand(() => navigate(item.to))}
                  className="flex cursor-pointer items-center gap-3 rounded-lg px-2.5 py-2.5 text-sm text-foreground aria-selected:bg-secondary"
                >
                  <item.icon size={16} className="text-muted-foreground" />
                  {item.label}
                </Command.Item>
              ))}
            </Command.Group>

            <Command.Group heading="Actions" className="mt-2 px-2 py-1.5 text-xs font-semibold text-muted-foreground [&_[cmdk-group-items]]:mt-1">
              <Command.Item
                onSelect={() => runCommand(toggleTheme)}
                className="flex cursor-pointer items-center gap-3 rounded-lg px-2.5 py-2.5 text-sm text-foreground aria-selected:bg-secondary"
              >
                {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
                Toggle theme
              </Command.Item>
              <Command.Item
                onSelect={() => runCommand(() => { logout(); navigate("/login"); })}
                className="flex cursor-pointer items-center gap-3 rounded-lg px-2.5 py-2.5 text-sm text-red-500 aria-selected:bg-red-500/10"
              >
                <LogOut size={16} />
                Log out
              </Command.Item>
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
