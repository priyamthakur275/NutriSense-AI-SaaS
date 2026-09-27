import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function CTABanner() {
  const navigate = useNavigate();

  return (
    <section className="px-6 py-16">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.6 }}
        className="relative mx-auto max-w-6xl overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/95 via-primary to-emerald-500 px-8 py-16 text-center shadow-2xl shadow-primary/20 md:px-16"
      >
        <div className="pointer-events-none absolute inset-0 bg-grid opacity-10" />
        <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 -right-20 h-64 w-64 rounded-full bg-black/10 blur-3xl" />

        <div className="relative">
          <h2 className="text-3xl font-bold tracking-tight text-primary-foreground md:text-4xl lg:text-5xl">
            Ready to automate nutrition
            <br className="hidden md:block" /> monitoring at your institution?
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-primary-foreground/85">
            Set up in minutes. No credit card required. Start with your existing
            canteen — scale to every institution you manage.
          </p>
          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button
              size="lg"
              onClick={() => navigate("/register")}
              className="bg-white text-primary shadow-lg hover:bg-white/90 hover:opacity-100"
            >
              Start free <ArrowRight size={16} />
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate("/login")}
              className="border-white/30 bg-transparent text-primary-foreground hover:bg-white/10"
            >
              Sign in
            </Button>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
