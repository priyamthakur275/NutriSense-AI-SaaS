import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, Settings, LifeBuoy, LogOut } from "lucide-react";
import {
  Dropdown,
  DropdownTrigger,
  DropdownContent,
  DropdownItem,
  DropdownLabel,
  DropdownSeparator,
} from "@/components/ui/Dropdown";
import { Avatar, AvatarFallback } from "@/components/ui/Avatar";
import { useAuthStore } from "@/store/authStore";
import { LogoutConfirmModal } from "@/components/layout/LogoutConfirmModal";

function initials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export function ProfileDropdown() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [logoutOpen, setLogoutOpen] = useState(false);

  return (
    <>
      <Dropdown>
        <DropdownTrigger asChild>
          <button
            aria-label="Account menu"
            className="flex items-center gap-2 rounded-lg border border-border p-1 pr-2.5 transition-colors hover:bg-secondary"
          >
            <Avatar className="h-7 w-7">
              <AvatarFallback className="text-xs">
                {user?.fullName ? initials(user.fullName) : "U"}
              </AvatarFallback>
            </Avatar>
            <span className="hidden text-sm font-medium sm:inline">
              {user?.fullName?.split(" ")[0] ?? "User"}
            </span>
          </button>
        </DropdownTrigger>
        <DropdownContent align="end" className="w-64">
          <div className="px-2.5 py-2">
            <p className="truncate text-sm font-semibold">{user?.fullName ?? "User"}</p>
            <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
          </div>
          <DropdownSeparator />
          <DropdownLabel className="sr-only">Account</DropdownLabel>
          <DropdownItem onSelect={() => navigate("/dashboard/settings")}>
            <User size={15} className="text-muted-foreground" /> Profile
          </DropdownItem>
          <DropdownItem onSelect={() => navigate("/dashboard/settings")}>
            <Settings size={15} className="text-muted-foreground" /> Settings
          </DropdownItem>
          <DropdownItem>
            <LifeBuoy size={15} className="text-muted-foreground" /> Support
          </DropdownItem>
          <DropdownSeparator />
          <DropdownItem
            onSelect={() => setLogoutOpen(true)}
            className="text-red-500 focus:bg-red-500/10 focus:text-red-500"
          >
            <LogOut size={15} /> Log out
          </DropdownItem>
        </DropdownContent>
      </Dropdown>

      <LogoutConfirmModal open={logoutOpen} onOpenChange={setLogoutOpen} />
    </>
  );
}
