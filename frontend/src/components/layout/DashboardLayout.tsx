import { Sidebar } from "@/components/layout/Sidebar";
import { DashboardHeader } from "@/components/layout/DashboardHeader";
import { MobileNav } from "@/components/layout/MobileNav";
import { CommandPalette } from "@/components/layout/CommandPalette";
import { FloatingActionButton } from "@/components/layout/FloatingActionButton";
import { PageTransition } from "@/components/layout/PageTransition";

export function DashboardLayout() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <MobileNav />
      <CommandPalette />

      <div className="flex flex-1 flex-col overflow-hidden">
        <DashboardHeader />
        <main className="flex-1 overflow-y-auto bg-secondary/30 p-6 md:p-8 lg:p-10">
          <div className="mx-auto max-w-7xl">
            <PageTransition />
          </div>
        </main>
      </div>

      <FloatingActionButton />
    </div>
  );
}
