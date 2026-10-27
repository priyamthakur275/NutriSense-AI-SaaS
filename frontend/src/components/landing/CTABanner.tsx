import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export function CTABanner() {
  const navigate = useNavigate();

  return (
    <section className="px-5 py-20 md:px-8">
      <div className="mx-auto grid max-w-7xl items-end gap-10 rounded-[28px] bg-sidebar ring-1 ring-black/5 dark:ring-white/10 px-8 py-14 md:grid-cols-[1.4fr_1fr] md:px-14 md:py-16">
        <div>
          <h2 className="font-display text-[2.2rem] font-extrabold leading-[1.02] tracking-[-0.03em] text-[#F5F7F2] md:text-5xl">
            Scan your first tray today.
          </h2>
          <p className="mt-5 max-w-lg text-lg leading-relaxed text-sidebar-muted">
            Create an account, add your institution and log a meal. The dashboard fills in as
            trays come through.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row md:justify-end">
          <Button
            size="lg"
            onClick={() => navigate("/register")}
            className="h-12 bg-[#E3A21A] px-6 text-[15px] text-[#12261D] hover:bg-[#EDB43C] hover:opacity-100"
          >
            Create a free account
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate("/login")}
            className="h-12 border-white/20 bg-transparent px-6 text-[15px] text-[#F5F7F2] hover:bg-white/10"
          >
            Sign in
          </Button>
        </div>
      </div>
    </section>
  );
}
