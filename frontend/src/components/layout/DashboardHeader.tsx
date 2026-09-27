import { Moon, Sun, Search, Menu } from "lucide-react";
import { useThemeStore } from "@/store/themeStore";
import { useUIStore } from "@/store/uiStore";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { NotificationsDropdown } from "@/components/layout/NotificationsDropdown";
import { ProfileDropdown } from "@/components/layout/ProfileDropdown";

export function DashboardHeader() {
  const { theme, toggleTheme } = useThemeStore();
  const { setCommandPaletteOpen, setMobileNavOpen } = useUIStore();

  return (
    <header className="flex h-16 flex-shrink-0 items-center gap-4 border-b border-border bg-background px-4 md:px-6">
      <button
        onClick={() => setMobileNavOpen(true)}
        aria-label="Open menu"
        className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg border border-border md:hidden"
      >
        <Menu size={16} />
      </button>

      <div className="hidden md:block">
        <Breadcrumbs />
      </div>

      <button
        onClick={() => setCommandPaletteOpen(true)}
        className="ml-0 flex h-9 flex-1 items-center gap-2 rounded-lg border border-border bg-secondary/40 px-3 text-sm text-muted-foreground transition-colors hover:bg-secondary md:ml-4 md:max-w-sm"
      >
        <Search size={14} />
        <span className="hidden sm:inline">Search or jump to...</span>
        <span className="sm:hidden">Search</span>
        <kbd className="ml-auto hidden items-center gap-0.5 rounded border border-border bg-background px-1.5 py-0.5 text-[10px] font-medium sm:flex">
          ⌘K
        </kbd>
      </button>

      <div className="ml-auto flex items-center gap-2.5">
        <button
          onClick={toggleTheme}
          aria-label="Toggle theme"
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-border transition-colors hover:bg-secondary"
        >
          {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
        </button>

        <NotificationsDropdown />
        <ProfileDropdown />
      </div>
    </header>
  );
}
